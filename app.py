import streamlit as st
import google.generativeai as genai
import requests
import io
from PIL import Image

# 1. SETUP PAGE CONFIGURATION
st.set_page_config(page_title="Cultural AI Photographer", page_icon="🌍")

# 2. SIDEBAR - API KEYS (So you don't hardcode them)
st.sidebar.header("Configuration")
st.sidebar.info("Enter your free API keys to start.")
gemini_key = st.sidebar.text_input("Gemini API Key", type="password")
hf_token = st.sidebar.text_input("Hugging Face Token", type="password")

# 3. THE "BRAIN" - GEMINI CULTURAL ANALYST
def get_cultural_prompt(country, occasion, user_desc):
    if not gemini_key:
        return None
    
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-2.0-flash') # Fast & Free
    
    # This prompt tells Gemini to act as a cultural consultant
    prompt = f"""
    Act as a professional cultural photographer and anthropologist.
    User wants a photo for: {occasion}
    Country/Culture: {country}
    User Description: {user_desc}
    
    Task: Write a HIGHLY DETAILED image generation prompt for Stable Diffusion. 
    Include specific details about:
    1. Traditional clothing (names of garments) suitable for this specific occasion in this country.
    2. The background (culturally accurate landmarks, decor, or scenery).
    3. Lighting and mood (nostalgic, festive, serious).
    4. Facial expression (appropriate for the culture and occasion).
    
    Output ONLY the prompt text in English. Do not add explanations.
    """
    
    response = model.generate_content(prompt)
    return response.text

# 4. THE "ARTIST" - HUGGING FACE API
def generate_image(prompt_text):
    if not hf_token:
        return None
        
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {hf_token}"}
    
    # Query the API
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt_text})
    
    if response.status_code == 200:
        return response.content
    else:
        st.error(f"Image generation failed: {response.text}")
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

# Upload Photo (For the MVP, we describe the user, later we face swap)
st.info("For this free Beta, we generate a new person based on your description. (Face Swap requires paid GPU).")
user_desc = f"A photorealistic {age} year old {gender} with average build"

if st.button("Generate Cultural Photo"):
    if not gemini_key or not hf_token:
        st.warning("Please enter your API keys in the sidebar first!")
    else:
        with st.spinner("consulting cultural experts..."):
            # Step 1: Get the magic prompt
            magic_prompt = get_cultural_prompt(country, occasion, user_desc)
            st.success("Cultural Context Found!")
            with st.expander("See the AI Prompt"):
                st.write(magic_prompt)
            
        with st.spinner("taking the photograph... (this takes ~10 seconds)"):
            # Step 2: Generate Image
            image_bytes = generate_image(magic_prompt)
            
            if image_bytes:
                image = Image.open(io.BytesIO(image_bytes))
                st.image(image, caption=f"Your {occasion} in {country}", use_column_width=True)
                
                # Step 3: The Nostalgic Message
                st.markdown(f"**Cultural Note:** In {country}, this style represents dignity and tradition.")
