import streamlit as st
from groq import Groq
import os
from pydub import AudioSegment
import tempfile

st.set_page_config(page_title="AI Meeting Secretary", layout="centered")

st.title("🎙️ AI Meeting Secretary")
st.write("Tải file ghi âm (.mp3, .wav, .m4a) để chuyển thành văn bản.")

# ====== GROQ CLIENT ======
api_key = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=api_key)

# ====== UPLOAD FILE ======
uploaded_file = st.file_uploader("Chọn file audio", type=["mp3", "wav", "m4a"])

if uploaded_file:

    st.info("🔄 Đang chuẩn hóa audio về 16kHz mono...")

    # Save file tạm
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    # Convert sang 16kHz mono WAV
    audio = AudioSegment.from_file(tmp_path)
    audio = audio.set_frame_rate(16000).set_channels(1)

    converted_path = tmp_path + "_converted.wav"
    audio.export(converted_path, format="wav")

    st.success("✅ Đã chuẩn hóa xong!")

    # ====== TRANSCRIBE ======
    st.info("🎧 Đang chuyển giọng nói thành văn bản bằng Groq Whisper...")

    with open(converted_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3",
            response_format="verbose_json"
        )

    st.success("✅ Đã chuyển giọng nói thành văn bản!")

    text_output = transcription.text

    st.subheader("📄 Nội dung chuyển đổi:")
    st.write(text_output)

    # ====== TẠO BIÊN BẢN ======
    if st.button("📋 Tạo biên bản"):
        st.info("🤖 Đang tạo biên bản cuộc họp...")

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "Bạn là thư ký doanh nghiệp. Hãy tạo biên bản cuộc họp chuyên nghiệp, rõ ràng, có: Tổng quan, Thảo luận chính, Quyết định, Phân công nhiệm vụ."
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