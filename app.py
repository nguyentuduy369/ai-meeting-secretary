import streamlit as st
import google.generativeai as genai
from datetime import datetime
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

# ===============================
# CONFIG
# ===============================

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

FREE_LIMIT = 10

st.set_page_config(page_title="Thư Ký AI SaaS", layout="centered")
st.title("📑 Thư Ký AI SaaS PRO (Gemini)")

# ===============================
# SESSION
# ===============================

if "usage" not in st.session_state:
    st.session_state.usage = 0

if "history" not in st.session_state:
    st.session_state.history = []

# ===============================
# SIDEBAR
# ===============================

st.sidebar.header("💳 Gói sử dụng")
remaining = FREE_LIMIT - st.session_state.usage
st.sidebar.write(f"Lượt miễn phí còn: {remaining}")

if st.sidebar.button("Nâng cấp 99k/tháng"):
    st.sidebar.success("Demo thanh toán thành công.")

# ===============================
# TEMPLATE
# ===============================

template = st.selectbox(
    "Chọn loại cuộc họp:",
    [
        "Họp Marketing",
        "Họp Nội Bộ",
        "Họp Chiến Lược",
        "Họp Startup",
        "Họp Báo Cáo KPI"
    ]
)

# ===============================
# INPUT
# ===============================

st.subheader("📥 Nhập nội dung hoặc tải Audio")

meeting_text = st.text_area("Nhập nội dung cuộc họp:", height=200)

audio_file = st.file_uploader("Hoặc tải file audio (.mp3, .wav)", type=["mp3", "wav"])

# ===============================
# AUDIO TRANSCRIBE (Gemini)
# ===============================

def transcribe_audio(file):

    audio_bytes = file.read()

    response = model.generate_content(
        [
            {
                "mime_type": file.type,
                "data": audio_bytes
            },
            "Hãy chuyển toàn bộ nội dung audio thành văn bản tiếng Việt rõ ràng."
        ]
    )

    return response.text

# ===============================
# GENERATE MINUTES
# ===============================

def generate_minutes(text):

    today = datetime.now().strftime("%d/%m/%Y")

    prompt = f"""
Bạn là thư ký doanh nghiệp chuyên nghiệp.

Tạo biên bản họp chuẩn doanh nghiệp cho loại: {template}

Yêu cầu:
- Trang trọng
- Tạo bảng KPI
- Tạo bảng phân công
- Tự tạo deadline nếu có
- Trình bày rõ ràng từng mục

Ngày họp: {today}

Nội dung:
{text}
"""

    response = model.generate_content(prompt)
    return response.text

# ===============================
# MAIN BUTTON
# ===============================

if st.button("🚀 Tạo Biên Bản"):

    if remaining <= 0:
        st.error("Bạn đã hết lượt miễn phí.")
        st.stop()

    if audio_file:
        with st.spinner("Đang chuyển audio thành text..."):
            meeting_text = transcribe_audio(audio_file)

    if meeting_text:

        with st.spinner("AI đang tạo biên bản..."):
            result = generate_minutes(meeting_text)

        st.session_state.usage += 1

        st.subheader("📄 Biên Bản")
        st.write(result)

        st.session_state.history.append({
            "time": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "content": result
        })

        # ===============================
        # EXPORT PDF
        # ===============================

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("<b>BIÊN BẢN HỌP</b>", styles["Title"]))
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(Paragraph(result.replace("\n", "<br/>"), styles["Normal"]))

        doc.build(elements)
        buffer.seek(0)

        st.download_button(
            "⬇️ Tải PDF",
            buffer,
            file_name="Bien_Ban_Hop.pdf",
            mime="application/pdf"
        )

# ===============================
# HISTORY
# ===============================

st.divider()
st.subheader("📚 Lịch sử họp")

for item in reversed(st.session_state.history):
    with st.expander(item["time"]):
        st.write(item["content"])