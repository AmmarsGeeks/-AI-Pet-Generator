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
st.set_page_config(page_title="AI PET Customization Advisor", page_icon="🐶✨", layout="wide")