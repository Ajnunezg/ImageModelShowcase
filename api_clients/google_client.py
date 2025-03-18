
import os
import json
import requests
from base64 import b64decode

def generate_image_google(prompt, api_key=None):
    """
    Generate an image using Google's Imagen 3 through Gemini API
    
    Args:
        prompt: Text prompt for image generation
        api_key: Google API key (optional, will use env var if not provided)
        
    Returns:
        dict: Dictionary containing image data or error
    """
    try:
        # Use provided API key or get from environment
        api_key = api_key or os.environ.get('GOOGLE_API_KEY')
        
        # Google Gemini API endpoint for Imagen
        url = "https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0:generateContent"
        
        # Request headers and parameters
        headers = {
            "Content-Type": "application/json",
        }
        
        # Add API key as a query parameter
        url = f"{url}?key={api_key}"
        
        # Request body
        data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generation_config": {
                "temperature": 0.4,
                "topP": 1.0,
                "topK": 32
            }
        }
        
        # Make API request
        response = requests.post(url, headers=headers, json=data)
        
        # Check if request was successful
        if response.status_code == 200:
            response_json = response.json()
            
            # Extract image data
            for candidate in response_json.get('candidates', []):
                for part in candidate.get('content', {}).get('parts', []):
                    if 'inlineData' in part:
                        # Extract and decode base64 image data
                        image_data = b64decode(part['inlineData']['data'])
                        return {"image_data": image_data}
            
            return {"error": "No image data found in the response"}
        else:
            return {"error": f"Google API error: {response.status_code} - {response.text}"}
    
    except Exception as e:
        return {"error": f"Google API error: {str(e)}"}
