from flask import Flask, request, jsonify
import requests
import os
from flask_cors import CORS

app = Flask(__name__)

# Retrieve API Key securely from environment variables
GEMINI_API_KEY = os.getenv('AIzaSyBHh8a7RMpIK9LrIgkXwf4sozLxibN1YcQ')

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    user_input = data.get('message')

    if not GEMINI_API_KEY:
        return jsonify({'error': 'API key not set'}), 500

    # Gemini API URL
    gemini_url = "https://api.gemini.com/v1/chat"

    headers = {
        'Authorization': f'Bearer {GEMINI_API_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        'input': user_input
    }
    print("payload")
    try:
        print("reply")
        gemini_response = requests.post(gemini_url, headers=headers, json=payload)
        gemini_response.raise_for_status()
        response_data = gemini_response.json()
        return jsonify({'response': response_data.get('output', 'No response from Gemini')})
        # data = request.json
        # user_message = data.get('message', '')
        # reply = f"Received your message: {user_message}"
        # print(reply)
        # return jsonify({'reply': reply})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    CORS(app) 
