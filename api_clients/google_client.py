import os
import google.generativeai as genai
from google.genai import types
from base64 import b64decode
import re

def generate_image_google(prompt, api_key=None):
    """
    Generate an image using Google's Gemini API

    Args:
        prompt: Text prompt for image generation
        api_key: Google API key (optional, will use env var if not provided)

    Returns:
        dict: Dictionary containing image data or error
    """
    try:
        # Use provided API key or get from environment
        api_key = api_key or os.environ.get('GOOGLE_API_KEY')

        # Initialize Gemini client
        genai.configure(api_key=api_key)
        client = genai.Client()

        # Prepare the prompt for image generation
        image_prompt = f"Generate an image: {prompt}"

        # Make API request
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=image_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["Image"]
            )
        )

        # Extract base64 image data from response
        if hasattr(response, 'parts') and response.parts:
            for part in response.parts:
                if hasattr(part, 'data') and part.data:
                    # Extract base64 data from the response
                    b64_data = re.search(r'base64,(.+)', part.data).group(1)
                    image_data = b64decode(b64_data)
                    return {"image_data": image_data}

        return {"error": "No image data found in the response"}

    except Exception as e:
        return {"error": f"Google API error: {str(e)}"}