import streamlit as st
import os
from datetime import datetime, timedelta
import glob
from deep_translator import GoogleTranslator
import re
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import login

# Set fixed current date
CURRENT_DATE = datetime(2025, 1, 30)

# Hugging Face authentication
def authenticate_huggingface():
    """Authenticate with Hugging Face using token"""
    # Get token from Streamlit secrets or environment variable
    hf_token = st.secrets.get("HUGGINGFACE_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")

    if not hf_token:
        st.error("Hugging Face token not found. Please set HUGGINGFACE_TOKEN in secrets or environment variables.")
        st.stop()

    try:
        login(token=hf_token)
        st.success("Successfully authenticated with Hugging Face!")
    except Exception as e:
        st.error(f"Failed to authenticate with Hugging Face: {str(e)}")
        st.stop()

# Initialize Mixtral model
@st.cache_resource
def load_mixtral_model():
    """Load Mixtral model with authentication"""
    try:
        tokenizer = AutoTokenizer.from_pretrained(
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            token=st.secrets.get("HUGGINGFACE_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
        )
        model = AutoModelForCausalLM.from_pretrained(
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            token=st.secrets.get("HUGGINGFACE_TOKEN") or os.getenv("HUGGINGFACE_TOKEN"),
            device_map="auto"
        )
        return model, tokenizer
    except Exception as e:
        st.error(f"Failed to load Mixtral model: {str(e)}")
        st.stop()

# [Previous functions remain the same]

def main():
    st.title("સમાચાર લેખ શોધ")

    # Authenticate with Hugging Face
    authenticate_huggingface()

    # Display current date
    st.write(f"વર્તમાન તારીખ: {CURRENT_DATE.strftime('%d-%m-%Y')}")

    # Load Mixtral model
    model, tokenizer = load_mixtral_model()

    # Rest of the code remains the same...

if __name__ == "__main__":
    main()
