import streamlit as st
import tempfile
import os
from dotenv import load_dotenv
from pydub import AudioSegment
from openai import OpenAI
from PIL import Image
import requests
from gtts import gTTS
from audio_recorder_streamlit import audio_recorder

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Check if API key is correctly set
if not os.getenv("OPENAI_API_KEY"):
    st.error("API Key is not set. Please check your .env file and ensure the OPENAI_API_KEY is correctly configured.")

# Streamlit app layout
st.set_page_config(page_title="AI PET Generator Advisor", page_icon="🐶✨", layout="wide")


# --- HEADER ---
st.markdown("""
    <div class="header">
        <h1>🐶✨ AI-Powered PET Generator Advisor</h1>
        <p> 🎧 Record Your Voice & Meet Your Dream Pet! </p>
    </div>
""", unsafe_allow_html=True)



# Function to transcribe speech to text using OpenAI Whisper API
def transcribe_audio(audio_file):
    audio = AudioSegment.from_file(audio_file)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        audio.export(tmp_file, format="wav")
        tmp_file_path = tmp_file.name

    try:
        with open(tmp_file_path, "rb") as audio_file:
            transcription_result = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )

        os.remove(tmp_file_path)
        return transcription_result.text

    except Exception as e:
        st.error(f"Transcription failed: {e}")
        return "Error in transcription"

# Function to generate car customization suggestions using OpenAI GPT
def generate_pet_description(transcription):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that creates unique and imaginative pet descriptions from user input."},
            {"role": "user", "content": transcription}
        ]
    )
    return response.choices[0].message.content

# Function to generate car image using DALL-E
def generate_pet_image(prompt):
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    image_url = response.data[0].url
    image_response = requests.get(image_url)
    with open("dream_pet.jpg", "wb") as f:
        f.write(image_response.content)
    return "dream_pet.jpg"




# --- RECORD AUDIO FEATURE ---
st.markdown("### 🎧 Record Your Own Voice")


audio_bytes = audio_recorder(pause_threshold=60.0, text="Click to Record")
if audio_bytes:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio_file:
        temp_audio_file.write(audio_bytes)
        temp_audio_file_path = temp_audio_file.name

    st.audio(audio_bytes, format="audio/mp3")

    transcription = transcribe_audio(temp_audio_file_path).strip()
    st.markdown(f"<div class='custom-card'><h3>📝 Transcription</h3><p>{transcription}</p></div>", unsafe_allow_html=True)

    if st.button("Generate Pet and Image"):
        description = generate_pet_description(transcription)
        st.markdown("<div class='custom-card'><h3>🐾 Pet Description</h3>", unsafe_allow_html=True)
        for line in description.split("\n"):
            st.markdown(f"- {line}")
        st.markdown("</div>", unsafe_allow_html=True)

        image_prompt = f"A dream pet with the following features: {transcription}"
        st.markdown("<div class='custom-card'><h3>🖼️ AI-Generated Pet Image</h3>", unsafe_allow_html=True)
        with st.spinner('Generating pet image...'):
            pet_image_path = generate_pet_image(image_prompt)
        pet_image = Image.open(pet_image_path)
        st.image(pet_image, caption="Your AI-Generated Pet")

        tts = gTTS(text=description, lang="en")
        tts.save("pet_description_audio.mp3")

        with open("pet_description_audio.mp3", "rb") as audio_file:
            st.audio(audio_file.read(), format="audio/mp3")

else:
    st.warning("Click the record button to start recording your voice.")



# --- UPLOAD AUDIO FILE FEATURE ---
st.markdown("### 📂 Browse and Upload Your Audio File")
audio_file = st.file_uploader("Choose an audio file...", type=["wav", "mp3", "flac"])


if audio_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
        temp_file.write(audio_file.read())
        audio_file_path = temp_file.name

    st.audio(audio_file, format="audio/wav")

    transcription = transcribe_audio(audio_file_path).strip()
    st.markdown(f"<div class='custom-card'><h3>📝 Transcription</h3><p>{transcription}</p></div>", unsafe_allow_html=True)

    if st.button("Generate Pet and Image", key='upload_btn'):
        description = generate_pet_description(transcription)
        st.markdown("<div class='custom-card'><h3>🐾 Pet Description</h3>", unsafe_allow_html=True)
        for line in description.split("\n"):
            st.markdown(f"- {line}")
        st.markdown("</div>", unsafe_allow_html=True)

        image_prompt = f"A dream pet with the following features: {transcription}"
        st.markdown("<div class='custom-card'><h3>🖼️ AI-Generated Pet Image</h3>", unsafe_allow_html=True)
        with st.spinner('Generating pet image...'):
            pet_image_path = generate_pet_image(image_prompt)
        pet_image = Image.open(pet_image_path)
        st.image(pet_image, caption="Your AI-Generated Pet")

        tts = gTTS(text=description, lang="en")
        tts.save("pet_description_audio.mp3")

        with open("pet_description_audio.mp3", "rb") as audio_file:
            st.audio(audio_file.read(), format="audio/mp3")



st.markdown("""
    <div class='footer'>
        Developed by ahammouch.xyz
    </div>
""", unsafe_allow_html=True)