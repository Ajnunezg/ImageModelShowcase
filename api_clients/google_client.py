import os
import json
import requests
from base64 import b64decode

def generate_image_google(prompt, api_key=None):
    """
    Generate an image using Google's Imagen 3 (imagen-3.0-generate-002) through Gemini API

    Args:
        prompt: Text prompt for image generation
        api_key: Google API key (optional, will use env var if not provided)

    Returns:
        dict: Dictionary containing image data or error
    """
    try:
        # Use provided API key or get from environment
        api_key = api_key or os.environ.get('GOOGLE_API_KEY')

        if not api_key:
            return {"error": "API key not provided or found in environment variables."}

        # Google Gemini API endpoint for Imagen 3 with API key as query parameter
        url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:generateContent?key={api_key}"

        # Request headers
        headers = {
            "Content-Type": "application/json"
        }

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
        elif response.status_code == 401:
            return {"error": f"Google API error: Unauthorized (401). Check your API key and restrictions."}
        elif response.status_code == 400:
            return {"error": f"Google API error: Bad Request (400). Check the request payload. {response.text}"}
        else:
            return {"error": f"Google API error: {response.status_code} - {response.text}"}

    except requests.exceptions.RequestException as e:
        return {"error": f"Request error: {str(e)}"}
    except json.JSONDecodeError as e:
        return {"error": f"JSON decode error: {str(e)} - {response.text}"}
    except Exception as e:
        return {"error": f"Google API error: {str(e)}"}

# Test the function
if __name__ == "__main__":
    result = generate_image_google("A cute kitten", api_key="YOUR_API_KEY_HERE")
    print(result)