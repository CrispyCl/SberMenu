import json
from requests import post

data = {
    "user": {
        "email": "gera@mail.ru",
        "password": "ggg",
        "role": "2"
    },
    "order": [
        1,
        0
    ]
}

a = post("http://127.0.0.1:8080/api/create_order", json=data)
print(a.json())