import streamlit as st
import requests
import tempfile
import os

# =============================
# CẤU HÌNH
# =============================
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

st.set_page_config(page_title="Thư Ký AI", page_icon="🎙️")

st.title("🎙️ Thư Ký AI - Ghi Âm & Văn Bản")
st.write("Chuyển giọng nói thành văn bản • Tóm tắt • Tạo biên bản")

# =============================
# HÀM CHUYỂN AUDIO → TEXT
# =============================
def transcribe_audio(file):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    files = {
        "file": file,
        "model": (None, "whisper-large-v3")
    }

    response = requests.post(GROQ_URL, headers=headers, files=files)

    if response.status_code == 200:
        return response.json()["text"]
    else:
        return f"Lỗi API: {response.text}"


# =============================
# HÀM TÓM TẮT
# =============================
def summarize_text(text):
    return f"""
📌 TÓM TẮT NỘI DUNG:

{text[:500]}...

(Kết thúc bản tóm tắt demo)
"""


# =============================
# GIAO DIỆN CHỌN CHẾ ĐỘ
# =============================
option = st.radio(
    "Chọn chế độ sử dụng:",
    ["🎧 Upload Audio", "📝 Nhập Văn Bản"]
)

st.divider()

# =============================
# CHẾ ĐỘ AUDIO
# =============================
if option == "🎧 Upload Audio":

    uploaded_file = st.file_uploader(
        "Tải file ghi âm (MP3, WAV, M4A)",
        type=["mp3", "wav", "m4a"]
    )

    if uploaded_file is not None:

        st.info("⏳ Đang chuyển giọng nói thành văn bản...")

        text = transcribe_audio(uploaded_file)

        st.success("✅ Đã chuyển giọng nói thành văn bản!")

        st.subheader("📄 Nội dung chuyển đổi:")
        st.text_area("Kết quả", text, height=300)

        if st.button("📌 Tóm tắt nội dung"):
            summary = summarize_text(text)
            st.text_area("Bản tóm tắt", summary, height=250)

        st.download_button(
            "⬇️ Tải file TXT",
            text,
            file_name="noi_dung.txt"
        )

# =============================
# CHẾ ĐỘ NHẬP TEXT
# =============================
elif option == "📝 Nhập Văn Bản":

    input_text = st.text_area(
        "Nhập nội dung cần xử lý:",
        height=300
    )

    if input_text:

        if st.button("📌 Tóm tắt nội dung"):
            summary = summarize_text(input_text)
            st.text_area("Bản tóm tắt", summary, height=250)

        if st.button("📝 Tạo Biên Bản Họp"):

            bien_ban = f"""
BIÊN BẢN HỌP

Nội dung:
{input_text}

Kết luận:
- Thống nhất triển khai theo kế hoạch.
- Phân công nhiệm vụ cụ thể.
- Theo dõi và báo cáo định kỳ.

(Kết thúc biên bản)
"""
            st.text_area("Biên bản", bien_ban, height=300)

            st.download_button(
                "⬇️ Tải Biên Bản TXT",
                bien_ban,
                file_name="bien_ban_hop.txt"
            )