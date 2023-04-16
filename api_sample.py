import requests
import json
import datetime

url = 'http://localhost:5000/api/task/0'
headers = {'Content-Type': 'application/json'}
data = {
    "maraphone_id": 1, "name": "PostTask",
    "date": datetime.date.today().strftime("%Y.%m.%d"),
    "description": "---", 'api_key': 'key'}
response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.json())