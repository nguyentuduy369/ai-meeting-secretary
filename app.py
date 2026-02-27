import streamlit as st
import google.generativeai as genai
import os
from datetime import datetime

st.set_page_config(page_title="AI Thư Ký Cuộc Họp", layout="centered")

st.title("📝 AI Thư Ký Doanh Nghiệp")

# Lấy API key từ Secrets
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)

# Lấy thời gian hiện tại
now = datetime.now()
formatted_time = now.strftime("%H:%M, ngày %d/%m/%Y")

st.subheader("Chọn cách nhập nội dung")

option = st.radio("Nguồn dữ liệu:", ["Dán nội dung", "Tải file ghi âm"])

meeting_text = ""

if option == "Dán nội dung":
    meeting_text = st.text_area("Nội dung cuộc họp", height=300)

elif option == "Tải file ghi âm":
    uploaded_file = st.file_uploader("Tải file (.mp3, .wav, .m4a)", type=["mp3","wav","m4a"])
    
    if uploaded_file:
        st.info("Đang xử lý file âm thanh...")
        model = genai.GenerativeModel("gemini-2.5-flash")
        audio_bytes = uploaded_file.read()
        
        response = model.generate_content([
            {"mime_type": uploaded_file.type, "data": audio_bytes},
            "Chuyển toàn bộ nội dung âm thanh này thành văn bản tiếng Việt."
        ])
        
        meeting_text = response.text
        st.success("Đã chuyển giọng nói thành văn bản!")
        st.text_area("Nội dung chuyển đổi", meeting_text, height=200)

if st.button("Tạo biên bản") and meeting_text:

    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
    Bạn là thư ký doanh nghiệp chuyên nghiệp.

    Thời gian họp: {formatted_time}

    Hãy tạo biên bản gồm:
    1. Tổng quan
    2. Quyết định chính
    3. Nhiệm vụ được giao
    4. Người phụ trách
    5. Deadline (nếu có)

    Nội dung:
    {meeting_text}
    """

    result = model.generate_content(prompt)

    st.subheader("📋 Biên bản cuộc họp")
    st.write(result.text)

elif not api_key:
    st.error("Chưa cấu hình GEMINI_API_KEY trong Streamlit Secrets.")