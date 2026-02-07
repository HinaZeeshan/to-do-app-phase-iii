
import requests
import uuid
import sys

BASE_URL = "http://localhost:8000/api"

def test_backend_flow():
    # 1. Signup
    email = f"test_{uuid.uuid4()}@example.com"
    password = "Password123!"
    print(f"Testing with email: {email}")

    signup_url = f"{BASE_URL}/auth/signup"
    print(f"POST {signup_url}")
    try:
        resp = requests.post(signup_url, json={"email": email, "password": password})
        print(f"Signup Status: {resp.status_code}")
        if resp.status_code not in [200, 201]:
            print(f"Signup Failed: {resp.text}")
            return
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    signup_data = resp.json()
    token = signup_data.get("token")
    user_id = signup_data.get("user_id")
    print(f"Signup Success. User ID: {user_id}")

    # 2. Login (to verify login works separately)
    login_url = f"{BASE_URL}/auth/login"
    print(f"POST {login_url}")
    resp = requests.post(login_url, json={"email": email, "password": password})
    print(f"Login Status: {resp.status_code}")
    if resp.status_code != 200:
        print(f"Login Failed: {resp.text}")
        return
    
    login_data = resp.json()
    token = login_data.get("token") # Refresh token if needed
    
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Create Task
    tasks_url = f"{BASE_URL}/{user_id}/tasks"
    print(f"POST {tasks_url}")
    task_payload = {"title": "My Python Test Task"}
    resp = requests.post(tasks_url, json=task_payload, headers=headers)
    print(f"Create Task Status: {resp.status_code}")
    if resp.status_code not in [200, 201]:
        print(f"Create Task Failed: {resp.text}")
        return

    task_data = resp.json()
    task_id = task_data.get("id")
    print(f"Task Created. ID: {task_id}")

    # 4. Update Task
    update_url = f"{BASE_URL}/{user_id}/tasks/{task_id}"
    print(f"PUT {update_url}")
    update_payload = {"title": "Updated Task Title", "is_completed": True}
    resp = requests.put(update_url, json=update_payload, headers=headers)
    print(f"Update Task Status: {resp.status_code}")
    
    # 5. Get Tasks
    print(f"GET {tasks_url}")
    resp = requests.get(tasks_url, headers=headers)
    print(f"Get Tasks Status: {resp.status_code}")
    print(f"Tasks: {resp.json().get('data', [])}")

    # 6. Delete Task
    delete_url = f"{BASE_URL}/{user_id}/tasks/{task_id}"
    print(f"DELETE {delete_url}")
    resp = requests.delete(delete_url, headers=headers)
    print(f"Delete Task Status: {resp.status_code}")

    print("\nBackend Validation Complete - Success!")

if __name__ == "__main__":
    test_backend_flow()
