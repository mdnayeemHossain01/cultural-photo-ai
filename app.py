import streamlit as st
import google.generativeai as genai
import requests
import io
from PIL import Image

# 1. PAGE CONFIG
st.set_page_config(page_title="Cultural AI Photographer", page_icon="🌍")

# 2. SIDEBAR
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Gemini API Key", type="password")
hf_token = st.sidebar.text_input("Hugging Face Token", type="password")

# 3. SMART MODEL SELECTOR (The Fix)
def get_gemini_response(prompt):
    if not api_key:
        return None
    
    genai.configure(api_key=api_key)
    
    # Try these models in order until one works
    models_to_try = ['gemini-1.5-flash', 'gemini-pro', 'gemini-1.5-pro-latest']
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text # If successful, return and stop trying
        except Exception:
            continue # If failed, try the next model in the list
            
    return "ERROR: All AI models are busy or unavailable. Please check your API key."

# 4. IMAGE GENERATION
def generate_image(prompt_text):
    if not hf_token:
        return None
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {hf_token}"}
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt_text})
        if response.status_code == 200:
            return response.content
        else:
            st.error("Hugging Face is busy. Try again in 30 seconds.")
            return None
    except:
        return None

# 5. UI
st.title("🌍 LocalLens: Cultural AI Studio")
col1, col2 = st.columns(2)
with col1:
    country = st.text_input("Country", "Japan")
    occasion = st.text_input("Occasion", "Wedding")
with col2:
    age = st.slider("Age", 18, 80, 25)
    gender = st.selectbox("Gender", ["Male", "Female"])

if st.button("Generate Photo"):
    if not api_key or not hf_token:
        st.warning("Please enter your API keys!")
    else:
        with st.spinner("Consulting cultural expert (Gemini)..."):
            # Create the prompt for Gemini
            prompt = f"Create a stable diffusion prompt for a photorealistic portrait of a {age} year old {gender} in {country} for a {occasion}. Describe clothing, background, and lighting in detail."
            
            # Get result from the "Smart Selector"
            magic_prompt = get_gemini_response(prompt)
            
        if "ERROR" in magic_prompt:
            st.error(magic_prompt)
        else:
            st.success(f"Context found! Generating image...")
            with st.spinner("Developing photo..."):
                image_bytes = generate_image(magic_prompt)
                if image_bytes:
                    st.image(Image.open(io.BytesIO(image_bytes)))
