import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="AI Thư Ký Cuộc Họp", layout="centered")

st.title("📝 AI Thư Ký Doanh Nghiệp")
st.write("Dán nội dung cuộc họp để tạo biên bản chuyên nghiệp.")

meeting_text = st.text_area("Nội dung cuộc họp", height=300)

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

if st.button("Tạo biên bản") and meeting_text and api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-pro")

    prompt = f"""
    Bạn là thư ký doanh nghiệp chuyên nghiệp.
    Hãy phân tích nội dung cuộc họp sau và tạo biên bản gồm:
    1. Tổng quan
    2. Quyết định chính
    3. Nhiệm vụ được giao
    4. Người phụ trách
    5. Deadline (nếu có)

    Nội dung:
    {meeting_text}
    """

    response = model.generate_content(prompt)

    st.subheader("📋 Biên bản cuộc họp")
    st.write(response.text)
