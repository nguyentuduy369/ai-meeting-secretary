import streamlit as st
import requests
from datetime import datetime
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

# ===============================
# CONFIG
# ===============================

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
AUDIO_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

MODEL = "llama3-8b-8192"
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
# AUDIO TRANSCRIPTION
# ===============================

def transcribe_audio(file):

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    files = {
        "file": (file.name, file, file.type),
        "model": (None, "whisper-large-v3")
    }

    response = requests.post(AUDIO_URL, headers=headers, files=files)

    if response.status_code == 200:
        return response.json()["text"]
    else:
        return f"Lỗi chuyển audio: {response.text}"

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

Ngày họp: {today}

Nội dung:
{text}
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Bạn là thư ký doanh nghiệp."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    response = requests.post(CHAT_URL, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Lỗi API: {response.text}"

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