import requests
from io import BytesIO
from PIL import Image

def save_image_from_url(image_url):
    """
    Download image from URL and save to a BytesIO object
    
    Args:
        image_url: URL of the image to download
        
    Returns:
        bytes: Image data as bytes or None if failed
    """
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            # Convert to PIL Image and save as PNG
            image = Image.open(BytesIO(response.content))
            img_byte_arr = BytesIO()
            image.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()
        return None
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None

def save_image_from_bytes(image_data):
    """
    Convert image bytes to PNG format
    
    Args:
        image_data: Raw image data as bytes
        
    Returns:
        bytes: Image data as PNG bytes or None if failed
    """
    try:
        image = Image.open(BytesIO(image_data))
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
    except Exception as e:
        print(f"Error processing image: {e}")
        return None
