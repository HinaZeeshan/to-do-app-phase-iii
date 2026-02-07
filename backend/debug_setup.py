
import sqlite3
import requests
import json
import sys

def check_db():
    print("Checking Database Tables...")
    try:
        conn = sqlite3.connect('todo_local.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Tables found: {tables}")
        conn.close()
        return [t[0] for t in tables]
    except Exception as e:
        print(f"DB Check Failed: {e}")
        return []

def test_signup():
    print("\nTesting Signup Endpoint...")
    url = "http://localhost:8000/api/auth/signup"
    payload = {
        "email": "debug_user@example.com",
        "password": "DebugUser123"
    }
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Signup Request Failed: {e}")

if __name__ == "__main__":
    tables = check_db()
    if 'users' not in tables:
        print("CRITICAL: 'users' table missing!")
    else:
        test_signup()
