import requests
import json

def test_backend():
    """Test if VANIE backend is running and responsive"""
    
    print("🔍 Testing VANIE AI Backend...")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Health Check: PASS")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health Check: FAIL (Status: {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running!")
        print("   Please start the backend first:")
        print("   1. Run: python VANIE.py")
        print("   2. Or double-click: start_server_fixed.bat")
        return False
    except requests.exceptions.Timeout:
        print("❌ Backend timeout!")
        return False
    except Exception as e:
        print(f"❌ Health Check Error: {e}")
        return False
    
    print()
    
    # Test chat API
    try:
        test_data = {
            "message": "hello",
            "session_id": "test_session"
        }
        
        response = requests.post(
            'http://localhost:5000/api/chat',
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Chat API: PASS")
            result = response.json()
            print(f"   Status: {result.get('status')}")
            print(f"   Response: {result.get('response', 'No response')[:50]}...")
            print(f"   Intents: {result.get('metadata', {}).get('detected_intents', [])}")
        else:
            print(f"❌ Chat API: FAIL (Status: {response.status_code})")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Chat API Error: {e}")
        return False
    
    print()
    print("🎉 All tests passed! Backend is working correctly!")
    return True

if __name__ == "__main__":
    test_backend()
