import os
import requests
import json

def generate_image_ideogram(prompt, api_key=None):
    """
    Generate an image using Ideogram v2
    
    Args:
        prompt: Text prompt for image generation
        api_key: Ideogram API key (optional, will use env var if not provided)
        
    Returns:
        dict: Dictionary containing image URL or error
    """
    try:
        # Use provided API key or get from environment
        api_key = api_key or os.environ.get('IDEOGRAM_API_KEY')
        
        # Ideogram API endpoint
        url = "https://api.ideogram.ai/api/v1/images/generations"
        
        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Request parameters
        data = {
            "model": "model-2.0",
            "prompt": prompt,
            "width": 1024,
            "height": 1024,
            "style": "natural",
            "num_images": 1
        }
        
        # Make API request
        response = requests.post(url, headers=headers, json=data)
        
        # Check if request was successful
        if response.status_code == 200:
            response_json = response.json()
            
            # Extract image URL
            for generation in response_json.get('generations', []):
                if 'url' in generation:
                    return {"url": generation['url']}
            
            return {"error": "No image URL found in the response"}
        else:
            return {"error": f"Ideogram API error: {response.status_code} - {response.text}"}
    
    except Exception as e:
        return {"error": f"Ideogram API error: {str(e)}"}
