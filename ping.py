import requests

moodle_url = "http://localhost"  # Replace with your Moodle URL
token = "bd6e045b97cd2ee54cc61c10cb13f135"  # Replace with your web service token

params = {
    "wstoken": token,
    "wsfunction": "core_ping",
    "moodlewsrestformat": "json",
}

try:
    response = requests.post(f"{moodle_url}/webservice/rest/server.php", data=params)
    response.raise_for_status()
    print(response.text)
    print(response.status_code)
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")