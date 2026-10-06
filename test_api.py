import requests
import json
import time

url = "http://localhost:8000/api/ai/predict"
payload = {
    "survey_point_id": "test_point_01",
    "survey_image_id": "test_image_01",
    "image_url": "https://raw.githubusercontent.com/ultralytics/yolov5/master/data/images/zidane.jpg",
    "user_id": "tester"
}

try:
    print("Sending request to API with online link...")
    start_time = time.time()
    response = requests.post(url, json=payload, timeout=30)
    end_time = time.time()
    print("Time taken:", round(end_time - start_time, 2), "seconds")
    print("Status Code:", response.status_code)
    # in ra json de doc
    try:
        data = response.json()
        print("Response:", json.dumps(data, indent=2, ensure_ascii=False))
    except Exception:
        print("Response Text:", response.text)
except Exception as e:
    print("Error:", e)
