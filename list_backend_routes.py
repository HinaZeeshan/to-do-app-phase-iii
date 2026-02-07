import requests
import json

def list_routes():
    try:
        resp = requests.get("http://localhost:8000/openapi.json")
        if resp.status_code == 200:
            data = resp.json()
            paths = list(data.get("paths", {}).keys())
            print("Registered Routes:")
            for path in sorted(paths):
                print(f"  {path}")
        else:
            print(f"Failed to fetch openapi.json: {resp.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_routes()
