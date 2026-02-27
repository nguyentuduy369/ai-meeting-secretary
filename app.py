import streamlit as st
import google.generativeai as genai
import os
from datetime import datetime
from groq import Groq

# ==============================
# CẤU HÌNH TRANG
# ==============================
st.set_page_config(page_title="AI Thư Ký Doanh Nghiệp", layout="centered")

st.title("📝 AI Thư Ký Cuộc Họp (Groq + Gemini)")
st.write("Upload file ghi âm → Chuyển thành văn bản → Tạo biên bản chuyên nghiệp")

# ==============================
# API KEYS
# ==============================
gemini_key = os.getenv("GEMINI_API_KEY")
groq_key = os.getenv("GROQ_API_KEY")

if not gemini_key or not groq_key:
    st.error("Thiếu GEMINI_API_KEY hoặc GROQ_API_KEY trong Secrets.")
    st.stop()

genai.configure(api_key=gemini_key)
groq_client = Groq(api_key=groq_key)

# ==============================
# THỜI GIAN TỰ ĐỘNG
# ==============================
now = datetime.now()
formatted_time = now.strftime("%H:%M, ngày %d/%m/%Y")

st.subheader("Tải file ghi âm (.mp3, .wav, .m4a)")

uploaded_file = st.file_uploader("Chọn file audio", type=["mp3", "wav", "m4a"])

meeting_text = ""

# ==============================
# SPEECH TO TEXT (GROQ WHISPER)
# ==============================
if uploaded_file is not None:

    st.info("Đang chuyển giọng nói thành văn bản bằng Groq Whisper...")

    try:
        transcription = groq_client.audio.transcriptions.create(
            file=uploaded_file,
            model="whisper-large-v3",
            response_format="text",
            language="vi"
        )

        meeting_text = transcription

        st.success("Đã chuyển giọng nói thành văn bản!")
        st.text_area("Nội dung chuyển đổi:", meeting_text, height=200)

    except Exception as e:
        st.error(f"Lỗi STT: {e}")

# ==============================
# TẠO BIÊN BẢN BẰNG GEMINI
# ==============================
if st.button("📋 Tạo biên bản") and meeting_text:

    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
    Bạn là thư ký doanh nghiệp chuyên nghiệp.

    Thời gian họp: {formatted_time}

    Hãy tạo biên bản gồm:
    1. Tổng quan
    2. Các quyết định chính
    3. Nhiệm vụ được giao
    4. Người phụ trách
    5. Deadline (nếu có)

    Loại bỏ từ đệm như: ờ, à, thì...
    Viết chuyên nghiệp, rõ ràng.

    Nội dung:
    {meeting_text}
    """

    try:
        result = model.generate_content(prompt)

        st.subheader("📄 Biên bản cuộc họp")
        st.write(result.text)

    except Exception as e:
        st.error(f"Lỗi tạo biên bản: {e}")