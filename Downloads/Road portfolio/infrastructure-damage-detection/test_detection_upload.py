#!/usr/bin/env python
"""
Test the detection upload endpoint
"""
import requests
import os
from pathlib import Path
from PIL import Image
import io

# Create a simple test image
test_image_path = "test_image.jpg"
if not os.path.exists(test_image_path):
    # Create a dummy image
    img = Image.new('RGB', (640, 480), color='red')
    img.save(test_image_path)
    print(f"Created test image: {test_image_path}")

# Prepare the upload
url = "http://localhost:8000/api/detection/detect"
files = {
    'file': open(test_image_path, 'rb')
}
data = {
    'latitude': 28.5244,
    'longitude': 77.0855,
    'road_type': 'highway'
}

print(f"\nTesting detection endpoint: {url}")
print(f"Payload: {data}")
print(f"Files: {files}")

try:
    response = requests.post(url, files=files, data=data)
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Text: {response.text[:500]}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nSuccess!")
        print(f"Report ID: {result.get('report_id')}")
        print(f"Detections: {len(result.get('detections', []))} found")
    else:
        print(f"\nError: {response.status_code}")
        print(f"Details: {response.text}")
except Exception as e:
    print(f"\nError during request: {e}")
    import traceback
    traceback.print_exc()
finally:
    if 'files' in locals():
        for f in files.values():
            if hasattr(f, 'close'):
                f.close()
