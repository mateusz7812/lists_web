import json

import requests


class Requester:
    def __init__(self, addres: str = "http://core:7000"):
        self.addres = addres

    def make_request(self, data):
        try:
            r = requests.post(self.addres, data=json.dumps(data))
        except requests.ConnectionError:
            return {"info": "connection with database error"}
        if r.content:
            return json.loads(str(r.content, "utf-8"))
        else:
            raise Exception("lack of data")

