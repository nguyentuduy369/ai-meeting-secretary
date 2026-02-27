import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from datetime import datetime
import io

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics

# ===============================
# CONFIG
# ===============================

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

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
                "Chuyển toàn bộ audio thành văn bản tiếng Việt rõ ràng."
            ]
        )

        return response.text

    except ResourceExhausted:
        return "⚠️ Đã vượt quota Gemini. Vui lòng thử lại sau."

    except Exception as e:
        return f"Lỗi audio: {str(e)}"

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
- Tạo bảng KPI rõ ràng
- Tạo bảng phân công
- Tự thêm deadline nếu có
- Trình bày rõ ràng từng mục

Ngày họp: {today}

Nội dung:
{text}
"""

    try:
        response = model.generate_content(prompt)
        return response.text

    except ResourceExhausted:
        return "⚠️ Đã vượt quota Gemini."

    except Exception as e:
        return f"Lỗi AI: {str(e)}"

# ===============================
# EXPORT PDF DOANH NGHIỆP
# ===============================

def export_pdf(content):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    import os

font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

if os.path.exists(font_path):
    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
    font_name = "DejaVuSans"
else:
    font_name = "Helvetica"  # fallback local

    style = ParagraphStyle(
        name='NormalStyle',
        fontName='STSong-Light',
        fontSize=11,
        leading=16
    )

    title_style = ParagraphStyle(
        name='TitleStyle',
        fontName=font_name ,
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        fontSize=16,
        leading=20
    )

    elements = []

    # HEADER
    elements.append(Paragraph("CÔNG TY CỔ PHẦN ABC", title_style))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("BIÊN BẢN HỌP", title_style))
    elements.append(Spacer(1, 0.4 * inch))

    # CONTENT
    paragraphs = content.split("\n")

    for p in paragraphs:
        elements.append(Paragraph(p, style))
        elements.append(Spacer(1, 0.15 * inch))

    # FOOTER TABLE
    elements.append(Spacer(1, 0.5 * inch))

    footer_data = [
        ["Chủ trì cuộc họp", "Thư ký cuộc họp"],
        ["(Ký, ghi rõ họ tên)", "(Ký, ghi rõ họ tên)"]
    ]

    table = Table(footer_data, colWidths=[3 * inch, 3 * inch])

    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'STSong-Light'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black)
    ]))

    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    return buffer

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

        pdf_file = export_pdf(result)

        st.download_button(
            "⬇️ Tải PDF Chuẩn Doanh Nghiệp",
            pdf_file,
            file_name="Bien_Ban_Hop_Doanh_Nghiep.pdf",
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