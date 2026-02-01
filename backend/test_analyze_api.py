import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_analyze(filename):
    print(f"Testing analyze for: {filename}")
    url = f"{BASE_URL}/analyze"
    params = {"video_filename": filename}
    
    try:
        response = requests.post(url, params=params)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Success!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_filename = sys.argv[1] if len(sys.argv) > 1 else "2024 All 22 Coach film Wk 01 Chiefs vs Ravens [7ERkAhvmHCo].mp4"
    test_analyze(test_filename)
