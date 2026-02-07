"""
Frontend verification script - Tests the frontend by checking HTML responses and API integration.
This script verifies that the frontend pages are accessible and properly configured.
"""

import requests
import uuid

FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://localhost:8000/api"

def test_frontend_pages():
    """Test that frontend pages are accessible."""
    print("=" * 60)
    print("FRONTEND PAGE ACCESSIBILITY TEST")
    print("=" * 60)
    
    pages = [
        "/",
        "/signup",
        "/login",
    ]
    
    for page in pages:
        url = f"{FRONTEND_URL}{page}"
        print(f"\nGET {url}")
        try:
            resp = requests.get(url, timeout=10)
            print(f"Status: {resp.status_code}")
            
            if resp.status_code == 200:
                # Check if it's HTML
                if 'text/html' in resp.headers.get('content-type', ''):
                    print(f"OK: Page loaded successfully (HTML response)")
                    # Check for key elements
                    if 'signup' in page and 'email' in resp.text.lower():
                        print("OK: Signup form elements detected")
                    elif 'login' in page and 'password' in resp.text.lower():
                        print("OK: Login form elements detected")
                else:
                    print(f"WARN: Non-HTML response: {resp.headers.get('content-type')}")
            else:
                print(f"FAIL: Failed with status {resp.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"X Request timed out after 10 seconds")
        except Exception as e:
            print(f"X Error: {e}")
    
    print("\n" + "=" * 60)

def test_frontend_backend_integration():
    """Test that frontend can communicate with backend."""
    print("\n" + "=" * 60)
    print("FRONTEND-BACKEND INTEGRATION TEST")
    print("=" * 60)
    
    # Create a test user via backend
    email = f"frontend_test_{uuid.uuid4()}@example.com"
    password = "FrontendTest123!"
    
    print(f"\n1. Creating test user via backend API")
    print(f"   Email: {email}")
    
    try:
        # Signup via backend
        signup_resp = requests.post(
            f"{BACKEND_URL}/auth/signup",
            json={"email": email, "password": password},
            timeout=5
        )
        
        if signup_resp.status_code == 201:
            print(f"   OK: User created successfully")
            data = signup_resp.json()
            token = data.get("token")
            user_id = data.get("user_id")
            
            # Test that frontend would be able to use this token
            print(f"\n2. Testing authenticated API call (simulating frontend)")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Create a task
            task_resp = requests.post(
                f"{BACKEND_URL}/{user_id}/tasks",
                json={"title": "Frontend Integration Test Task"},
                headers=headers,
                timeout=5
            )
            
            if task_resp.status_code == 201:
                print(f"   OK: Task created successfully (frontend would work)")
                task_id = task_resp.json().get("id")
                
                # Get tasks
                get_resp = requests.get(
                    f"{BACKEND_URL}/{user_id}/tasks",
                    headers=headers,
                    timeout=5
                )
                
                if get_resp.status_code == 200:
                    tasks = get_resp.json().get("data", [])
                    print(f"   OK: Retrieved {len(tasks)} task(s)")
                    
                    # Cleanup
                    requests.delete(
                        f"{BACKEND_URL}/{user_id}/tasks/{task_id}",
                        headers=headers,
                        timeout=5
                    )
                    print(f"   OK: Cleanup completed")
                else:
                    print(f"   FAIL: Failed to get tasks: {get_resp.status_code}")
            else:
                print(f"   FAIL: Failed to create task: {task_resp.status_code}")
        else:
            print(f"   FAIL: Failed to create user: {signup_resp.status_code}")
            print(f"   Response: {signup_resp.text}")
            
    except Exception as e:
        print(f"   FAIL: Error: {e}")
    
    print("\n" + "=" * 60)

def check_frontend_config():
    """Check frontend configuration."""
    print("\n" + "=" * 60)
    print("FRONTEND CONFIGURATION CHECK")
    print("=" * 60)
    
    print("\nChecking .env.local file...")
    try:
        with open("h:/phase-iii/frontend/.env.local", "r") as f:
            env_content = f.read()
            print("OK: .env.local file exists")
            
            if "NEXT_PUBLIC_API_URL" in env_content:
                print("OK: NEXT_PUBLIC_API_URL is configured")
                # Extract the value
                for line in env_content.split('\n'):
                    if line.startswith('NEXT_PUBLIC_API_URL'):
                        print(f"  Value: {line.split('=')[1].strip()}")
            else:
                print("WARN: NEXT_PUBLIC_API_URL not found in .env.local")
                
    except FileNotFoundError:
        print("⚠ .env.local file not found")
    except Exception as e:
        print(f"✗ Error reading config: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("FRONTEND VERIFICATION SCRIPT")
    print("=" * 60)
    print("\nThis script tests:")
    print("1. Frontend page accessibility")
    print("2. Frontend-backend integration")
    print("3. Frontend configuration")
    print("\n" + "=" * 60)
    
    # Run tests
    test_frontend_pages()
    test_frontend_backend_integration()
    check_frontend_config()
    
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)
    print("\nFor full UI testing, please manually test in browser:")
    print(f"  -> Open {FRONTEND_URL} in your browser")
    print("  → Test signup, login, and task management features")
    print("=" * 60 + "\n")
