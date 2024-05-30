import unittest
import requests

class Test(unittest.TestCase):
    def test_add_user(self):
        url = "http://127.0.0.1:5000/api/v1.0/admin/add_user"
        resp = requests.post(url)
        print(resp.json())

        resp = requests.post(url, json={"username": "lady_killer12345"})
        print(resp.json())

        resp = requests.post(url, json={"username": "lady_killer9","phone_number":"123456789"})
        print(resp.json())

        resp = requests.post(url, json={"username": "lady_killer9", "phone_number": "13456789291"})
        print(resp.json())

    # 测试get_user_info api
    def test_get_user_info(self):
        url = "http://127.0.0.1:5000/api/v1.0/get_user_info"
        resp = requests.post(url)
        print(resp.json())

        resp = requests.post(url, json={"username": "lady_killer12345678qweasdzxc"})
        print(resp.json())

        resp = requests.post(url, json={"username": "lady_killer0"})
        print(resp.json())

        resp = requests.post(url, json={"username": "lady_killer9"})
        print(resp.json())