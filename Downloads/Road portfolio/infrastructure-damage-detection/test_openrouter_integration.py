#!/usr/bin/env python3
"""
Test script to verify Open Router API integration
"""

import os
import sys
import asyncio
import httpx
import json
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
env_file = Path(__file__).parent / ".env"
load_dotenv(env_file)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
OPENROUTER_API_URL = os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions")


async def test_openrouter_connection():
    """Test the Open Router API connection"""
    
    print("=" * 60)
    print("🧪 Testing Open Router API Integration")
    print("=" * 60)
    print()
    
    # Check configuration
    print("📋 Configuration Check:")
    print(f"  API Key loaded: {'✓' if OPENROUTER_API_KEY else '✗ MISSING'}")
    print(f"  Model: {OPENROUTER_MODEL}")
    print(f"  API URL: {OPENROUTER_API_URL}")
    print()
    
    if not OPENROUTER_API_KEY:
        print("❌ ERROR: OPENROUTER_API_KEY not found in .env file!")
        return False
    
    # Test API connection
    print("🔗 Testing API Connection...")
    
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "RoadGuard Infrastructure Damage Detection",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are RoadGuard AI Assistant, an expert infrastructure damage analysis assistant."
                },
                {
                    "role": "user",
                    "content": "What is a pothole?"
                }
            ],
            "temperature": 0.7,
            "max_tokens": 200,
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                OPENROUTER_API_URL,
                json=payload,
                headers=headers
            )
            
            print(f"  Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if "choices" in data and len(data["choices"]) > 0:
                    reply = data["choices"][0]["message"]["content"]
                    print(f"  ✓ API Connection Successful!")
                    print()
                    print("💬 Test Response:")
                    print(f"  {reply[:200]}...")
                    print()
                    print("✅ Open Router Integration is WORKING!")
                    return True
                else:
                    print(f"  ✗ Unexpected response format: {data}")
                    return False
            else:
                print(f"  ✗ API Error: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
                
    except httpx.TimeoutException:
        print("  ✗ Request Timeout - Check your internet connection")
        return False
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False


async def test_infrastructure_analysis():
    """Test with infrastructure damage analysis context"""
    
    print()
    print("=" * 60)
    print("🧪 Testing with Infrastructure Analysis Context")
    print("=" * 60)
    print()
    
    if not OPENROUTER_API_KEY:
        print("❌ Skipping - No API key configured")
        return False
    
    try:
        analysis_context = {
            "detections": [
                {"damage_type": "pothole", "severity": "moderate", "location": "Lane 1"},
                {"damage_type": "crack", "severity": "severe", "location": "Lane 2"}
            ],
            "summary": {
                "total_estimated_cost": 50000
            }
        }
        
        system_prompt = f"""You are RoadGuard AI Assistant. Analyze this infrastructure damage:
        
{json.dumps(analysis_context, indent=2)}

Provide a brief summary of the damage found."""
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "RoadGuard Infrastructure Damage Detection",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": "What damage was detected?"
                }
            ],
            "temperature": 0.7,
            "max_tokens": 300,
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                OPENROUTER_API_URL,
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    reply = data["choices"][0]["message"]["content"]
                    print("✓ Analysis Context Test Successful!")
                    print()
                    print("📊 AI Response:")
                    print(reply)
                    print()
                    print("✅ Infrastructure Analysis Integration WORKING!")
                    return True
            
        return False
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def main():
    """Run all tests"""
    
    test1 = await test_openrouter_connection()
    test2 = await test_infrastructure_analysis()
    
    print()
    print("=" * 60)
    print("📋 Test Summary")
    print("=" * 60)
    print(f"  Connection Test: {'✅ PASSED' if test1 else '❌ FAILED'}")
    print(f"  Analysis Test: {'✅ PASSED' if test2 else '❌ FAILED'}")
    print()
    
    if test1 and test2:
        print("🎉 All tests PASSED! Your Open Router integration is ready to use.")
        print()
        print("Next steps:")
        print("  1. Run: python run_backend.py")
        print("  2. Visit: http://localhost:3000")
        print("  3. Upload an image to test the AI chat")
        return 0
    else:
        print("⚠️  Some tests failed. Check your API key and internet connection.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
