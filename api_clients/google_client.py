
import os
import json
import requests
from base64 import b64decode

def generate_image_google(prompt, api_key=None):
    """
    Generate an image using Google's Vertex AI
    
    Args:
        prompt: Text prompt for image generation
        api_key: Google API key (optional, will use env var if not provided)
        
    Returns:
        dict: Dictionary containing image data or error
    """
    try:
        # Use provided API key or get from environment
        api_key = api_key or os.environ.get('GOOGLE_API_KEY')
        
        # Google Vertex AI endpoint
        url = "https://us-central1-aiplatform.googleapis.com/v1/projects/PROJECT_ID/locations/us-central1/publishers/google/models/imagegeneration:predict"
        
        # Request headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Request body
        data = {
            "instances": [{
                "prompt": prompt
            }],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "1:1",
                "negativePrompt": "",
                "seed": 0
            }
        }
        
        # Make API request
        response = requests.post(url, headers=headers, json=data)
        
        # Check if request was successful
        if response.status_code == 200:
            response_json = response.json()
            
            # Extract image data
            if 'predictions' in response_json and len(response_json['predictions']) > 0:
                image_b64 = response_json['predictions'][0]['bytesBase64Encoded']
                image_data = b64decode(image_b64)
                return {"image_data": image_data}
            
            return {"error": "No image data found in the response"}
        else:
            return {"error": f"Google API error: {response.status_code} - {response.text}"}
    
    except Exception as e:
        return {"error": f"Google API error: {str(e)}"}
