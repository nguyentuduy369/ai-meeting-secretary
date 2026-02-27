import streamlit as st
import google.generativeai as genai
import os
import io
from datetime import datetime

# ===== REPORTLAB =====
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import pagesizes
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics


# ==============================
# CONFIG API KEY (ỔN ĐỊNH)
# ==============================
def get_api_key():
    if "GOOGLE_API_KEY" in st.secrets:
        return st.secrets["GOOGLE_API_KEY"]
    return os.getenv("GOOGLE_API_KEY")


api_key = get_api_key()

if not api_key:
    st.error("Không tìm thấy GOOGLE_API_KEY. Vui lòng kiểm tra Secrets hoặc biến môi trường.")
    st.stop()

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")


# ==============================
# HÀM TẠO PDF CHUẨN DOANH NGHIỆP
# ==============================
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

    # ===== FIX FONT TIẾNG VIỆT =====
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
        font_name = "DejaVuSans"
    else:
        font_name = "Helvetica"

    # ===== STYLE =====
    style_company = ParagraphStyle(
        name="Company",
        fontName=font_name,
        fontSize=14,
        leading=18,
        alignment=1,
        spaceAfter=10
    )

    style_title = ParagraphStyle(
        name="Title",
        fontName=font_name,
        fontSize=16,
        leading=20,
        alignment=1,
        spaceAfter=20
    )

    style_normal = ParagraphStyle(
        name="NormalVN",
        fontName=font_name,
        fontSize=12,
        leading=16
    )

    # ===== HEADER =====
    elements.append(Paragraph("<b>CÔNG TY CỔ PHẦN ABC</b>", style_company))
    elements.append(Paragraph("<b>BIÊN BẢN HỌP</b>", style_title))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    elements.append(Spacer(1, 12))

    # ===== NỘI DUNG =====
    paragraphs = content_text.split("\n")

    for p in paragraphs:
        elements.append(Paragraph(p, style_normal))
        elements.append(Spacer(1, 6))

    elements.append(Spacer(1, 20))

    # ===== CHỮ KÝ =====
    signature_data = [
        ["ĐẠI DIỆN CHỦ TRÌ", "", "THƯ KÝ"],
        ["(Ký, ghi rõ họ tên)", "", "(Ký, ghi rõ họ tên)"]
    ]

    signature_table = Table(signature_data, colWidths=[200, 50, 200])

    signature_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 20),
        ("FONTNAME", (0, 0), (-1, -1), font_name),
    ]))

    elements.append(signature_table)

    doc.build(elements)

    buffer.seek(0)
    return buffer


# ==============================
# UI
# ==============================
st.set_page_config(page_title="Thư Ký AI Chuẩn Doanh Nghiệp")

st.title("📄 Thư Ký AI Chuẩn Doanh Nghiệp")
st.write("Tạo biên bản họp chuyên nghiệp từ nội dung cuộc họp.")

uploaded_file = st.file_uploader("Tải file nội dung cuộc họp (.txt)", type=["txt"])

if uploaded_file is not None:

    text_content = uploaded_file.read().decode("utf-8")

    with st.spinner("AI đang xử lý nội dung cuộc họp..."):

        prompt = f"""
        Bạn là Thư ký doanh nghiệp chuyên nghiệp.

        Hãy tạo biên bản họp đầy đủ gồm:
        - Thông tin cuộc họp
        - Thành phần tham dự
        - Nội dung thảo luận
        - Kết luận
        - Danh sách hành động (Action Items)
        - Deadline rõ ràng
        - Phân công trách nhiệm

        Nội dung cuộc họp:
        {text_content}
        """

        response = model.generate_content(prompt)
        meeting_minutes = response.text

    st.subheader("📌 Biên bản họp")
    st.text_area("", meeting_minutes, height=500)

    pdf_buffer = generate_enterprise_pdf(meeting_minutes)

    st.download_button(
        label="📥 Tải file PDF",
        data=pdf_buffer,
        file_name=f"Bien_Ban_Hop_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf"
    )