import requests
import json
import datetime

KEY = "you key"
URL = "http://localhost:5000"

# castom errors:
# 430 error - maraphone not found
# 432 error - task not found


def get_maraphone_by_id(maraphone_id):
    url = URL + '/api/maraphone/' + str(maraphone_id)
    headers = {'Content-Type': 'application/json'}
    data = {'api_key': KEY}
    response = requests.get(url, headers=headers, data=json.dumps(data))
    # {'maraphone': {'created_date': '-', 'creator_id': -, 'id': -, 'title': '-'}}
    return response.json()


def get_task_list(maraphone_id):
    url = URL + '/api/task_list/' + str(maraphone_id)
    headers = {'Content-Type': 'application/json'}
    data = {'api_key': KEY}
    response = requests.get(url, headers=headers, data=json.dumps(data))
    # {'tasks': [{'created_date': '-', 'date': '-', 'description': '-', 'id': -, 'main': {'creator_id': -}, 'main_id': -, 'name': '-'}]}
    # main_id = id пользователя, который сделал
    return response.json()


def get_task(task_id):
    url = URL + '/api/task/' + str(task_id)
    headers = {'Content-Type': 'application/json'}
    data = {'api_key': KEY}
    response = requests.get(url, headers=headers, data=json.dumps(data))
    # {'created_date': '-', 'date': '-', 'description': '-', 'id': -, 'main': {'creator_id': -}, 'main_id': -, 'name': '-'}
    # main_id = id пользователя, который сделал
    return response.json()


def post_task(maraphone_id, name, date, description):
    url = URL + '/api/task/0'
    headers = {
        'Content-Type': 'application/json'
        }
    data = {
        "maraphone_id": maraphone_id, "name": name,
        "date": date,
        "description": description, 'api_key': KEY}
    # date in format y.m.d
    # you can use .strftime("%Y.%m.%d") from datetime
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()