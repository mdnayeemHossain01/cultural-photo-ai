import streamlit as st
import google.generativeai as genai
import requests
import io
from PIL import Image

# 1. SETUP PAGE CONFIGURATION
st.set_page_config(page_title="Cultural AI Photographer", page_icon="🌍")

# 2. SIDEBAR - API KEYS
st.sidebar.header("Configuration")
st.sidebar.info("Enter your free API keys to start.")
gemini_key = st.sidebar.text_input("Gemini API Key", type="password")
hf_token = st.sidebar.text_input("Hugging Face Token", type="password")

# 3. THE "BRAIN" - GEMINI CULTURAL ANALYST
def get_cultural_prompt(country, occasion, user_desc):
    if not gemini_key:
        return None
    
    # Configure Gemini with the key
    genai.configure(api_key=gemini_key)
    
    # FIX: Using 'gemini-pro' (The most stable version)
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        Act as a professional cultural photographer.
        User wants a photo for: {occasion}
        Country/Culture: {country}
        User Description: {user_desc}
        
        Task: Write a HIGHLY DETAILED image generation prompt for Stable Diffusion. 
        Include specific details about:
        1. Traditional clothing suitable for this occasion.
        2. The background (landmarks or decor).
        3. Lighting and mood.
        
        Output ONLY the prompt text in English.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Gemini Error: {str(e)}")
        return None

# 4. THE "ARTIST" - HUGGING FACE API
def generate_image(prompt_text):
    if not hf_token:
        return None
        
    # We use Stable Diffusion XL (High Quality)
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {hf_token}"}
    
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt_text})
        
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"Image Error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

# 5. THE WEBSITE UI
st.title("🌍 LocalLens: Cultural AI Studio")
st.markdown("### Make yourself culturally surrounded.")

# Inputs
col1, col2 = st.columns(2)
with col1:
    country = st.text_input("Target Country/Culture", "Japan")
    occasion = st.text_input("Occasion (e.g., Wedding, Job)", "Job Application")
with col2:
    age = st.slider("Age", 18, 80, 25)
    gender = st.selectbox("Gender", ["Male", "Female", "Non-binary"])

# Description for the AI
user_desc = f"A photorealistic {age} year old {gender} with average build"

if st.button("Generate Cultural Photo"):
    if not gemini_key or not hf_token:
        st.warning("Please enter your API keys in the sidebar first!")
    else:
        # Step 1: Get the magic prompt
        with st.spinner("consulting cultural experts..."):
            magic_prompt = get_cultural_prompt(country, occasion, user_desc)
            
        if magic_prompt:
            st.success("Cultural Context Found!")
            with st.expander("See the AI Prompt"):
                st.write(magic_prompt)
            
            # Step 2: Generate Image
            with st.spinner("taking the photograph... (this takes ~10 seconds)"):
                image_bytes = generate_image(magic_prompt)
                
                if image_bytes:
                    image = Image.open(io.BytesIO(image_bytes))
                    st.image(image, caption=f"Your {occasion} in {country}", use_column_width=True)
                    st.markdown(f"**Cultural Note:** Custom style generated for {country}.")
