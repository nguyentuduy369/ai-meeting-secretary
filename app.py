import streamlit as st
import requests
from datetime import datetime
import json
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Image
from reportlab.lib.styles import getSampleStyleSheet
import io

# ===============================
# CONFIG
# ===============================

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"

FREE_LIMIT = 10
PRICE = "99.000 VNĐ / tháng"

st.set_page_config(page_title="Thư Ký AI SaaS", layout="centered")
st.title("📑 Thư Ký AI SaaS")

# ===============================
# SESSION STATE
# ===============================

if "usage_count" not in st.session_state:
    st.session_state.usage_count = 0

if "history" not in st.session_state:
    st.session_state.history = []

# ===============================
# SUBSCRIPTION SIMULATION
# ===============================

st.sidebar.header("💳 Gói sử dụng")

st.sidebar.write(f"Miễn phí còn lại: {FREE_LIMIT - st.session_state.usage_count}")

upgrade = st.sidebar.button("Nâng cấp gói 99k/tháng")

if upgrade:
    st.sidebar.success("Tính năng thanh toán demo. (Có thể tích hợp Momo sau)")

# ===============================
# TEMPLATE SELECT
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

meeting_text = st.text_area("Nhập nội dung cuộc họp:", height=250)

# ===============================
# AI FUNCTION
# ===============================

def generate_minutes(text, template_type):

    today = datetime.now().strftime("%d/%m/%Y")

    prompt = f"""
Bạn là thư ký doanh nghiệp chuyên nghiệp.

Tạo biên bản họp chuẩn doanh nghiệp cho loại: {template_type}

Yêu cầu:
- Loại bỏ tranh luận
- Chỉ giữ quyết định cuối
- Tạo bảng KPI
- Tạo bảng phân công
- Trình bày trang trọng

Ngày họp: {today}

Nội dung:
{text}
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "Bạn là thư ký doanh nghiệp."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    response = requests.post(GROQ_CHAT_URL, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Lỗi API: {response.text}"

# ===============================
# GENERATE
# ===============================

if st.button("🚀 Tạo Biên Bản"):

    if st.session_state.usage_count >= FREE_LIMIT:
        st.error("Bạn đã hết lượt miễn phí. Vui lòng nâng cấp gói.")
    elif meeting_text:

        with st.spinner("Đang xử lý..."):
            result = generate_minutes(meeting_text, template)

        st.session_state.usage_count += 1

        st.subheader("📄 Biên bản")
        st.write(result)

        # Save history
        st.session_state.history.append({
            "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
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
    with st.expander(f"📅 {item['date']}"):
        st.write(item["content"])