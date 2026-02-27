import streamlit as st
import google.generativeai as genai
import os
from datetime import datetime
import tempfile
import mimetypes

# ==============================
# CẤU HÌNH TRANG
# ==============================
st.set_page_config(page_title="AI Thư Ký Doanh Nghiệp", layout="centered")

st.title("📝 AI Thư Ký Cuộc Họp")
st.write("Ứng dụng tự động chuyển ghi âm thành biên bản chuyên nghiệp.")

# ==============================
# API KEY
# ==============================
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Chưa cấu hình GEMINI_API_KEY trong Streamlit Secrets.")
    st.stop()

genai.configure(api_key=api_key)

# ==============================
# THỜI GIAN TỰ ĐỘNG
# ==============================
now = datetime.now()
formatted_time = now.strftime("%H:%M, ngày %d/%m/%Y")

st.subheader("Chọn nguồn dữ liệu")

option = st.radio(
    "Nguồn nội dung:",
    ["Dán nội dung cuộc họp", "Tải file ghi âm"]
)

meeting_text = ""

# ==============================
# NHẬP TEXT
# ==============================
if option == "Dán nội dung cuộc họp":
    meeting_text = st.text_area("Nhập nội dung cuộc họp:", height=300)

# ==============================
# UPLOAD AUDIO (FIX MIME TYPE)
# ==============================
elif option == "Tải file ghi âm":

    uploaded_file = st.file_uploader(
        "Tải file (.mp3, .wav, .m4a)",
        type=["mp3", "wav", "m4a"]
    )

    if uploaded_file is not None:

        st.info("Đang xử lý file âm thanh...")

        # Lưu file tạm
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.read())
            temp_path = tmp_file.name

        # Xác định MIME type thủ công
        mime_type, _ = mimetypes.guess_type(uploaded_file.name)

        if mime_type is None:
            # fallback an toàn
            if uploaded_file.name.endswith(".wav"):
                mime_type = "audio/wav"
            elif uploaded_file.name.endswith(".mp3"):
                mime_type = "audio/mpeg"
            elif uploaded_file.name.endswith(".m4a"):
                mime_type = "audio/mp4"
            else:
                mime_type = "audio/wav"

        try:
            model = genai.GenerativeModel("gemini-2.5-flash")

            uploaded = genai.upload_file(
                path=temp_path,
                mime_type=mime_type
            )

            response = model.generate_content([
                uploaded,
                "Chuyển toàn bộ nội dung âm thanh này thành văn bản tiếng Việt rõ ràng."
            ])

            meeting_text = response.text

            st.success("Đã chuyển giọng nói thành văn bản!")
            st.text_area("Nội dung chuyển đổi:", meeting_text, height=200)

        except Exception as e:
            st.error(f"Lỗi xử lý audio: {e}")

# ==============================
# TẠO BIÊN BẢN
# ==============================
if st.button("📋 Tạo biên bản") and meeting_text:

    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
    Bạn là thư ký doanh nghiệp chuyên nghiệp.

    Thời gian họp: {formatted_time}

    Hãy tạo biên bản gồm:
    1. Tổng quan cuộc họp
    2. Các quyết định chính
    3. Nhiệm vụ được giao
    4. Người phụ trách
    5. Deadline (nếu có)

    Loại bỏ các từ đệm như: ờ, à, thì, kiểu...
    Viết lại ngắn gọn, chuyên nghiệp.

    Nội dung:
    {meeting_text}
    """

    try:
        result = model.generate_content(prompt)
        st.subheader("📄 Biên bản cuộc họp")
        st.write(result.text)

    except Exception as e:
        st.error(f"Lỗi tạo biên bản: {e}")