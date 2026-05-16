#!/usr/bin/env python
"""
Test detection upload exactly like the browser would with fetch API
"""
import requests
from PIL import Image
import json
import os

def test_detection_with_browser_like_request():
    """Test the /api/detection/detect endpoint with FormData like a browser would send"""
    
    # Create a test image
    test_image_path = "test_browser_upload.jpg"
    if not os.path.exists(test_image_path):
        img = Image.new('RGB', (640, 480), color='red')
        img.save(test_image_path)
        print(f"Created test image: {test_image_path}")
    
    url = "http://localhost:8000/api/detection/detect"
    
    try:
        # Test 1: Upload with browser-like FormData
        with open(test_image_path, 'rb') as f:
            # Simulate browser FormData append
            files = {'file': f}
            data = {
                'latitude': '28.5244',  # String to match FormData.append behavior
                'longitude': '77.0855',
                'road_type': 'highway'
            }
            
            print(f"\n{'='*60}")
            print("Test 1: Browser-like FormData upload")
            print(f"{'='*60}")
            print(f"URL: {url}")
            print(f"File: {test_image_path}")
            print(f"Metadata: {data}\n")
            
            response = requests.post(url, files=files, data=data)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Type: {response.headers.get('content-type')}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ SUCCESS!")
                print(f"   Report ID: {result.get('report_id')}")
                print(f"   Detections: {len(result.get('detections', []))} found")
                print(f"   Summary Cost: ₹{result['summary'].get('total_estimated_cost', 0)}")
                print(f"   Response Keys: {list(result.keys())}")
            else:
                print(f"\n❌ FAILED!")
                print(f"Response: {response.text[:500]}")
        
        # Test 2: Test the endpoint without GPS (optional fields)
        print(f"\n{'='*60}")
        print("Test 2: Detection without GPS metadata")
        print(f"{'='*60}\n")
        
        with open(test_image_path, 'rb') as f:
            response = requests.post(url, files={'file': f})
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ SUCCESS without metadata!")
                print(f"   Report ID: {result.get('report_id')}")
            else:
                print(f"❌ FAILED: {response.text[:200]}")
        
        # Test 3: Verify test-upload endpoint is available
        print(f"\n{'='*60}")
        print("Test 3: Test-upload endpoint verification")
        print(f"{'='*60}\n")
        
        with open(test_image_path, 'rb') as f:
            test_url = "http://localhost:8000/api/detection/test-upload"
            response = requests.post(test_url, files={'file': f}, data={
                'latitude': 28.5244,
                'longitude': 77.0855,
                'road_type': 'highway'
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Test endpoint available!")
                print(f"   File received: {result.get('file_received')}")
                print(f"   File name: {result.get('file_name')}")
                print(f"   Metadata received: lat={result.get('latitude_received')}, lon={result.get('longitude_received')}, road={result.get('road_type_received')}")
            else:
                print(f"❌ Test endpoint error: {response.status_code}")
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_detection_with_browser_like_request()
