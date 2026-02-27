import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
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

# Dùng model nhẹ hơn để tránh quota
model = genai.GenerativeModel("gemini-1.5-flash")

FREE_LIMIT = 10

st.set_page_config(page_title="Thư Ký AI SaaS", layout="centered")
st.title("📑 Thư Ký AI SaaS PRO")

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

meeting_text = st.text_area("Nhập nội dung cuộc họp:", height=200)
audio_file = st.file_uploader("Tải file audio (.mp3, .wav)", type=["mp3", "wav"])

# ===============================
# AUDIO TRANSCRIBE
# ===============================

def transcribe_audio(file):
    try:
        audio_bytes = file.read()

        response = model.generate_content(
            [
                {
                    "mime_type": file.type,
                    "data": audio_bytes
                },
                "Chuyển audio thành văn bản tiếng Việt."
            ]
        )

        return response.text

    except ResourceExhausted:
        return "⚠️ Đã vượt quota Gemini. Vui lòng chờ vài phút rồi thử lại."

    except Exception as e:
        return f"Lỗi audio: {str(e)}"

# ===============================
# GENERATE MINUTES
# ===============================

def generate_minutes(text):

    today = datetime.now().strftime("%d/%m/%Y")

    prompt = f"""
Bạn là thư ký doanh nghiệp chuyên nghiệp.

Tạo biên bản họp cho loại: {template}

- Tạo bảng KPI
- Tạo bảng phân công
- Tự thêm deadline nếu có
- Văn phong trang trọng

Ngày: {today}

Nội dung:
{text}
"""

    try:
        response = model.generate_content(prompt)
        return response.text

    except ResourceExhausted:
        return "⚠️ Đã vượt quota Gemini. Vui lòng thử lại sau."

    except Exception as e:
        return f"Lỗi AI: {str(e)}"

# ===============================
# MAIN BUTTON
# ===============================

if st.button("🚀 Tạo Biên Bản"):

    if remaining <= 0:
        st.error("Bạn đã hết lượt miễn phí.")
        st.stop()

    if audio_file:
        with st.spinner("Đang xử lý audio..."):
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

        # EXPORT PDF
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