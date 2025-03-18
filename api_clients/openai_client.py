import os
import requests
from openai import OpenAI

def generate_image_openai(prompt, api_key=None):
    """
    Generate an image using OpenAI's DALL-E 3
    
    Args:
        prompt: Text prompt for image generation
        api_key: OpenAI API key (optional, will use env var if not provided)
        
    Returns:
        dict: Dictionary containing image URL or error
    """
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key or os.environ.get('OPENAI_API_KEY'))
        
        # Call DALL-E 3 API
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="standard",
        )
        
        # Extract image URL
        image_url = response.data[0].url
        
        return {"url": image_url}
    
    except Exception as e:
        return {"error": f"OpenAI API error: {str(e)}"}
