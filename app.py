import streamlit as st
import os
import io
import time
import pandas as pd
from PIL import Image
import base64
from concurrent.futures import ThreadPoolExecutor
import asyncio

from api_clients.openai_client import generate_image_openai
from api_clients.google_client import generate_image_google
from api_clients.recraft_client import generate_image_recraft
from api_clients.ideogram_client import generate_image_ideogram
from utils import save_image_from_url, save_image_from_bytes

st.set_page_config(
    page_title="AI Image Generator Comparison",
    page_icon="🎨",
    layout="wide"
)

# Initialize session state
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = {}

if 'prompt' not in st.session_state:
    st.session_state.prompt = ""

if 'api_keys' not in st.session_state:
    st.session_state.api_keys = {
        'openai': os.environ.get('OPENAI_API_KEY', ''),
        'google': os.environ.get('GOOGLE_API_KEY', ''),
        'recraft': os.environ.get('RECRAFT_API_KEY', ''),
        'ideogram': os.environ.get('IDEOGRAM_API_KEY', '')
    }

if 'api_keys_set' not in st.session_state:
    st.session_state.api_keys_set = {
        'openai': False,
        'google': False,
        'recraft': False,
        'ideogram': False
    }

if 'loading' not in st.session_state:
    st.session_state.loading = False

def check_api_keys():
    """Check if API keys are available in session state or environment variables"""
    # First check session state for manually entered keys
    api_keys = {
        'openai': st.session_state.api_keys['openai'],
        'google': st.session_state.api_keys['google'],
        'recraft': st.session_state.api_keys['recraft'],
        'ideogram': st.session_state.api_keys['ideogram']
    }
    
    # Fallback to environment variables if session state keys are empty
    if not api_keys['openai']:
        api_keys['openai'] = os.environ.get('OPENAI_API_KEY', '')
    if not api_keys['google']:
        api_keys['google'] = os.environ.get('GOOGLE_API_KEY', '')
    if not api_keys['recraft']:
        api_keys['recraft'] = os.environ.get('RECRAFT_API_KEY', '')
    if not api_keys['ideogram']:
        api_keys['ideogram'] = os.environ.get('IDEOGRAM_API_KEY', '')
    
    # Update API keys set status
    for key, value in api_keys.items():
        st.session_state.api_keys_set[key] = bool(value)
    
    return api_keys

def generate_images(prompt):
    """Generate images from all enabled AI services"""
    st.session_state.loading = True
    st.session_state.generated_images = {}
    
    # Get the latest API keys
    api_keys = check_api_keys()
    
    # Define generator functions with their respective requirements
    generators = []
    if st.session_state.api_keys_set['openai']:
        generators.append(('OpenAI DALL-E 3', lambda: generate_image_openai(prompt, api_keys['openai'])))
    if st.session_state.api_keys_set['google']:
        generators.append(('Google Imagen 3', lambda: generate_image_google(prompt, api_keys['google'])))
    if st.session_state.api_keys_set['recraft']:
        generators.append(('Recraft AI', lambda: generate_image_recraft(prompt, api_keys['recraft'])))
    if st.session_state.api_keys_set['ideogram']:
        generators.append(('Ideogram v2', lambda: generate_image_ideogram(prompt, api_keys['ideogram'])))
    
    # Use ThreadPoolExecutor to run API calls in parallel
    results = {}
    if generators:
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all tasks and collect futures
            futures = {executor.submit(generator): name for name, generator in generators}
            
            # Process futures as they complete
            for future in futures:
                name = futures[future]
                try:
                    result = future.result()
                    results[name] = result
                except Exception as e:
                    results[name] = {'error': str(e)}
    else:
        st.error("No API keys configured. Please add at least one API key in the API Keys Configuration section.")
    
    st.session_state.generated_images = results
    st.session_state.loading = False

def main():
    st.title("AI Image Generator Comparison")
    
    with st.expander("API Keys Configuration", expanded=not any(st.session_state.api_keys_set.values())):
        st.markdown("""
        Enter your API keys for the image generation services you want to use.
        You only need to provide keys for the services you want to compare.
        Your API keys are stored securely in your session and are never shared.
        """)
        
        # Create input fields for each API key
        api_key_cols = st.columns(2)
        
        # Save API keys function
        def save_api_keys():
            check_api_keys()
            st.success("API keys saved successfully!")
        
        with api_key_cols[0]:
            st.subheader("OpenAI DALL-E 3")
            openai_key = st.text_input(
                "OpenAI API Key",
                type="password",
                value=st.session_state.api_keys["openai"],
                help="Get your API key from https://platform.openai.com/api-keys"
            )
            if openai_key != st.session_state.api_keys["openai"]:
                st.session_state.api_keys["openai"] = openai_key
            
            st.subheader("Google Imagen 3")
            google_key = st.text_input(
                "Google API Key",
                type="password",
                value=st.session_state.api_keys["google"],
                help="Get your API key from Google AI Studio"
            )
            if google_key != st.session_state.api_keys["google"]:
                st.session_state.api_keys["google"] = google_key
        
        with api_key_cols[1]:
            st.subheader("Recraft AI")
            recraft_key = st.text_input(
                "Recraft API Key",
                type="password",
                value=st.session_state.api_keys["recraft"],
                help="Get your API key from Recraft AI website"
            )
            if recraft_key != st.session_state.api_keys["recraft"]:
                st.session_state.api_keys["recraft"] = recraft_key
            
            st.subheader("Ideogram v2")
            ideogram_key = st.text_input(
                "Ideogram API Key",
                type="password",
                value=st.session_state.api_keys["ideogram"],
                help="Get your API key from Ideogram website"
            )
            if ideogram_key != st.session_state.api_keys["ideogram"]:
                st.session_state.api_keys["ideogram"] = ideogram_key
        
        # Save and check API keys button
        if st.button("Save and Check API Keys"):
            save_api_keys()
        
        # Display API key status
        st.subheader("API Key Status")
        check_api_keys()
        status_cols = st.columns(4)
        with status_cols[0]:
            st.write("OpenAI: ", "✅" if st.session_state.api_keys_set['openai'] else "❌")
        with status_cols[1]:
            st.write("Google: ", "✅" if st.session_state.api_keys_set['google'] else "❌")
        with status_cols[2]:
            st.write("Recraft: ", "✅" if st.session_state.api_keys_set['recraft'] else "❌")
        with status_cols[3]:
            st.write("Ideogram: ", "✅" if st.session_state.api_keys_set['ideogram'] else "❌")
    
    # Input prompt
    st.subheader("Enter your prompt")
    prompt = st.text_area("Image Generation Prompt", st.session_state.prompt, height=100)
    
    # Generate button
    generate_col, status_col = st.columns([2, 3])
    
    with generate_col:
        if st.button("Generate Images", disabled=not any(st.session_state.api_keys_set.values()) or not prompt):
            st.session_state.prompt = prompt
            generate_images(prompt)
    
    with status_col:
        if not any(st.session_state.api_keys_set.values()):
            st.warning("Please configure at least one API key to generate images.")
        elif not prompt:
            st.info("Enter a prompt to generate images.")
    
    # Display loading status
    if st.session_state.loading:
        st.markdown("### Generating images...")
        st.progress(0.75)
    
    # Display generated images
    if st.session_state.generated_images:
        st.markdown("### Generated Images")
        st.markdown(f"**Prompt:** {st.session_state.prompt}")
        
        # Create columns for each generated image
        cols = st.columns(len(st.session_state.generated_images))
        
        for i, (name, result) in enumerate(st.session_state.generated_images.items()):
            with cols[i]:
                st.markdown(f"#### {name}")
                
                if 'error' in result:
                    st.error(f"Error: {result['error']}")
                else:
                    try:
                        if 'url' in result:
                            # Display image from URL
                            st.image(result['url'], use_column_width=True)
                            
                            # Download button
                            image_data = save_image_from_url(result['url'])
                            if image_data:
                                st.download_button(
                                    label="Download",
                                    data=image_data,
                                    file_name=f"{name.lower().replace(' ', '_')}_{int(time.time())}.png",
                                    mime="image/png"
                                )
                        elif 'image_data' in result:
                            # Display image from bytes
                            image = Image.open(io.BytesIO(result['image_data']))
                            st.image(image, use_column_width=True)
                            
                            # Download button
                            st.download_button(
                                label="Download",
                                data=result['image_data'],
                                file_name=f"{name.lower().replace(' ', '_')}_{int(time.time())}.png",
                                mime="image/png"
                            )
                    except Exception as e:
                        st.error(f"Error displaying image: {str(e)}")

if __name__ == "__main__":
    main()
