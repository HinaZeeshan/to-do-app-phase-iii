
import requests

BASE_URL = "http://localhost:8000/api"

# Use the credentials from your successful manual test or create new ones
# For this script we'll just sign up a new user every time to be safe
def get_auth_token():
    try:
        # distinct email each time to avoid conflict
        import time
        email = f"tasktest_{int(time.time())}@example.com"
        
        response = requests.post(f"{BASE_URL}/auth/signup", json={
            "email": email,
            "password": "Password123!",
            "full_name": "Task Tester"
        })
        if response.status_code == 201:
            return response.json()["token"]
        else:
            print(f"Signup failed: {response.text}")
            return None
    except Exception as e:
        print(f"Auth error: {e}")
        return None

def test_create_task(token):
    print("\nTesting Task Creation...")
    try:
        # Decode token to get user_id
        import json
        import base64
        
        # Simple JWT decode without verification just to extract payload
        payload = token.split('.')[1]
        padded_payload = payload + '=' * (4 - len(payload) % 4)
        decoded_bytes = base64.urlsafe_b64decode(padded_payload)
        decoded_str = decoded_bytes.decode('utf-8')
        user_data = json.loads(decoded_str)
        user_id = user_data.get("user_id") or user_data.get("sub")
        
        print(f"Extracted User ID: {user_id}")
        
        headers = {"Authorization": f"Bearer {token}"}
        task_data = {
            "title": "Test Task",
            "description": "This is a test task",
            "completed": False,
            "is_completed": False # Add this just in case schema expects it
        }
        
        # Correct URL pattern: /api/{user_id}/tasks
        response = requests.post(f"{BASE_URL}/{user_id}/tasks", json=task_data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Task creation error: {e}")

if __name__ == "__main__":
    token = get_auth_token()
    if token:
        test_create_task(token)
