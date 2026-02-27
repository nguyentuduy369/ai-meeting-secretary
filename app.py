import streamlit as st
from groq import Groq
import tempfile

st.set_page_config(page_title="AI Meeting Secretary", layout="centered")

st.title("🎙️ AI Meeting Secretary")
st.write("Tải file ghi âm (.mp3, .wav, .m4a) để chuyển thành văn bản.")

# ====== GROQ CLIENT ======
api_key = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=api_key)

uploaded_file = st.file_uploader("Chọn file audio", type=["mp3", "wav", "m4a"])

if uploaded_file:

    st.info("🎧 Đang chuyển giọng nói thành văn bản bằng Groq Whisper...")

    # Lưu file tạm
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    with open(tmp_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            file=(uploaded_file.name, audio_file.read()),
            model="whisper-large-v3"
        )

    st.success("✅ Đã chuyển giọng nói thành văn bản!")

    text_output = transcription.text

    st.subheader("📄 Nội dung chuyển đổi:")
    st.write(text_output)

    if st.button("📋 Tạo biên bản"):
        st.info("🤖 Đang tạo biên bản cuộc họp...")

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "Bạn là thư ký doanh nghiệp. Hãy tạo biên bản cuộc họp chuyên nghiệp gồm: Tổng quan, Nội dung thảo luận, Quyết định, Phân công nhiệm vụ."
                },
                {
                    "role": "user",
                    "content": text_output
                }
            ]
        )

        meeting_minutes = completion.choices[0].message.content

        st.subheader("📝 Biên bản cuộc họp:")
        st.write(meeting_minutes)