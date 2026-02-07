import requests

BASE_URL = "http://localhost:8000"

def test_signup():
    print("Testing Signup...")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": "test@example.com",
            "password": "Password123!",
            "full_name": "Test User"
        })
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_login():
    print("\nTesting Login...")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@example.com",
            "password": "Password123!"
        })
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_options():
    print("\nTesting OPTIONS (CORS)...")
    try:
        # Test with likely mismatched origin
        response = requests.options(f"{BASE_URL}/api/auth/login", headers={
            "Origin": "http://127.0.0.1:3000", 
            "Access-Control-Request-Method": "POST"
        })
        print(f"Status: {response.status_code}")
        print(f"Headers: {response.headers}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_options()
    test_signup()
    test_login()
