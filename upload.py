import requests
import json

url = "http://localhost/grade/report/userperformance/upload.php"

data = [
    {"user_id": 3, "course_id": 2, "Performance": "Good"},
    {"user_id": 4, "course_id": 2, "Performance": "Average"}
]

headers = {'Content-Type': 'application/json'}
response = requests.post(url, data=json.dumps(data), headers=headers)

print(response.text)
