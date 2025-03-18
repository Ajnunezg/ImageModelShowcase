import os
import requests
from base64 import b64decode

def generate_image_recraft(prompt, api_key=None):
    """
    Generate an image using Recraft AI
    
    Args:
        prompt: Text prompt for image generation
        api_key: Recraft API key (optional, will use env var if not provided)
        
    Returns:
        dict: Dictionary containing image URL or error
    """
    try:
        # Use provided API key or get from environment
        api_key = api_key or os.environ.get('RECRAFT_API_KEY')
        
        # Recraft API endpoint
        url = "https://api.recraft.ai/creations"
        
        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Request parameters
        data = {
            "model": "sd3",
            "prompt": prompt,
            "width": 1024,
            "height": 1024
        }
        
        # Make API request
        response = requests.post(url, headers=headers, json=data)
        
        # Check if request was successful
        if response.status_code == 200:
            response_json = response.json()
            
            # Extract image URL
            if "url" in response_json:
                return {"url": response_json["url"]}
            else:
                return {"error": "No image URL found in the response"}
        else:
            return {"error": f"Recraft API error: {response.status_code} - {response.text}"}
    
    except Exception as e:
        return {"error": f"Recraft API error: {str(e)}"}
