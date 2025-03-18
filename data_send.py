import requests
import json

# Replace these variables with your actual values
MOODLE_URL = 'http://localhost'
MOODLE_TOKEN = 'your_moodle_webservice_token'

# JSON data
data = [
    {"user_id": 3, "course_id": 2, "Performance": "Average Performance"},
    {"user_id": 4, "course_id": 2, "Performance": "Poor Performance"},
    {"user_id": 5, "course_id": 2, "Performance": "Good Performance"},
    {"user_id": 3, "course_id": 3, "Performance": "Good Performance"},
    {"user_id": 4, "course_id": 3, "Performance": "Poor Performance"},
    {"user_id": 5, "course_id": 3, "Performance": "Average Performance"}
]

def send_performance_data(user_id, course_id, performance):
    endpoint = f'{MOODLE_URL}/webservice/rest/server.php'
    payload = {
        'wstoken': MOODLE_TOKEN,
        'wsfunction': 'local_userperformance_submit_performance',
        'moodlewsrestformat': 'json',
        'userid': user_id,
        'courseid': course_id,
        'performance': performance
    }

    response = requests.post(endpoint, data=payload)
    if response.status_code == 200:
        print(f'Successfully sent data for user_id: {user_id}, course_id: {course_id}')
    else:
        print(f'Failed to send data for user_id: {user_id}, course_id: {course_id}')
        print(response.text)

if __name__ == '__main__':
    for record in data:
        send_performance_data(record['user_id'], record['course_id'], record['Performance'])