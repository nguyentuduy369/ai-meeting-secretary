import streamlit as st
import google.generativeai as genai
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import pagesizes
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics
import io
import os

# =============================
# CẤU HÌNH TRANG
# =============================
st.set_page_config(
    page_title="Thư Ký AI Chuẩn Doanh Nghiệp",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Thư Ký AI Chuẩn Doanh Nghiệp")
st.write("Tạo biên bản họp chuyên nghiệp từ nội dung cuộc họp.")

# =============================
# API KEY (FIX TRIỆT ĐỂ)
# =============================

api_key = None

try:
    api_key = st.secrets.get("GOOGLE_API_KEY")
except Exception:
    api_key = None

if not api_key:
    api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    st.error("❌ Không tìm thấy GOOGLE_API_KEY.")
    st.info("Kiểm tra Streamlit → Manage App → Settings → Secrets")
    st.stop()

genai.configure(api_key=api_key)

# =============================
# MODEL GEMINI 2.5 FLASH
# =============================
model = genai.GenerativeModel("gemini-2.5-flash")

# =============================
# HÀM TẠO BIÊN BẢN
# =============================
def generate_minutes(meeting_text):

    prompt = f"""
Bạn là thư ký doanh nghiệp chuyên nghiệp.

Hãy tạo BIÊN BẢN HỌP chuẩn doanh nghiệp từ nội dung sau:

{meeting_text}

Yêu cầu:
- Văn phong chuyên nghiệp
- Có cấu trúc rõ ràng
- Có mục tiêu, nội dung, phân công công việc
- Có phần kết thúc và ký tên
- Viết hoàn chỉnh bằng tiếng Việt
"""

    response = model.generate_content(prompt)
    return response.text


# =============================
# HÀM TẠO PDF (KHÔNG LỖI FONT)
# =============================
def generate_enterprise_pdf(content_text):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=pagesizes.A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=50,
        bottomMargin=50
    )

    elements = []

    # Font Unicode có sẵn trong reportlab
    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))

    style_company = ParagraphStyle(
        name='Company',
        fontName='STSong-Light',
        fontSize=14,
        leading=18,
        alignment=1,
        spaceAfter=10
    )

    style_title = ParagraphStyle(
        name='Title',
        fontName='STSong-Light',
        fontSize=16,
        leading=20,
        alignment=1,
        spaceAfter=20
    )

    style_normal = ParagraphStyle(
        name='NormalVN',
        fontName='STSong-Light',
        fontSize=12,
        leading=16
    )

    # HEADER
    elements.append(Paragraph("<b>CÔNG TY CỔ PHẦN ABC</b>", style_company))
    elements.append(Paragraph("<b>BIÊN BẢN HỌP</b>", style_title))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    elements.append(Spacer(1, 12))

    # NỘI DUNG
    paragraphs = content_text.split("\n")
    for p in paragraphs:
        if p.strip():
            elements.append(Paragraph(p, style_normal))
            elements.append(Spacer(1, 6))

    elements.append(Spacer(1, 20))

    # KÝ TÊN
    signature_data = [
        ["ĐẠI DIỆN CHỦ TRÌ", "", "THƯ KÝ"],
        ["(Ký, ghi rõ họ tên)", "", "(Ký, ghi rõ họ tên)"]
    ]

    signature_table = Table(signature_data, colWidths=[200, 50, 200])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
    ]))

    elements.append(signature_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer


# =============================
# GIAO DIỆN NHẬP LIỆU
# =============================
st.subheader("📥 Nhập nội dung cuộc họp")

meeting_input = st.text_area(
    "Dán nội dung cuộc họp vào đây:",
    height=250
)

if st.button("🚀 Tạo Biên Bản"):

    if not meeting_input.strip():
        st.warning("Vui lòng nhập nội dung cuộc họp.")
    else:
        with st.spinner("Đang tạo biên bản..."):
            minutes = generate_minutes(meeting_input)

        st.subheader("📑 Biên Bản Họp")
        st.write(minutes)

        st.session_state["minutes"] = minutes


# =============================
# TẢI PDF
# =============================
if "minutes" in st.session_state:

    if st.button("📥 Tải PDF Chuẩn Doanh Nghiệp"):

        pdf_file = generate_enterprise_pdf(st.session_state["minutes"])

        st.download_button(
            label="Tải xuống PDF",
            data=pdf_file,
            file_name="Bien_Ban_Hop_Doanh_Nghiep.pdf",
            mime="application/pdf"
        )