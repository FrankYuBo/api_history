import unittest
import requests
import random
import uuid
import hashlib
import hmac
import json

from requests.auth import HTTPBasicAuth
from services.auth_service import save_nonce_with_expiry,check_nonce

class Test(unittest.TestCase):
    def test_digest_auth(self):
        from requests.auth import HTTPDigestAuth
        resp = requests.post("http://127.0.0.1:5000/api/v2.0/admin/digest_auth/add_user",json={"username": "lady_killer9", "phone_number": "13456789291"}
                             ,auth=HTTPDigestAuth(username='test',password='test'))
        print(resp.json())

    def test_redis(self):
        key = str(uuid.uuid4())
        save_nonce_with_expiry(key,1,5*60)
        res = check_nonce(key)
        print(res)

    def test_hmac(self):
        url = "http://127.0.0.1:5000/api/v2.0/admin/hmac/add_user"
        signature = "no nonce and username signature will not check"
        headers = {
            "Signature": signature
        }
        response = requests.post(url, headers=headers,
                                 json={"username": "lady_killer9", "phone_number": "13456789291"})
        print(response.json())

        url = f"http://127.0.0.1:5000/api/v2.0/admin/hmac/add_user?username=admin&nonce={random.randint(0,2**32)}"
        signature = "wrong signature"
        headers = {
            "Signature": signature
        }
        response = requests.post(url, headers=headers,
                                 json={"username": "lady_killer9", "phone_number": "13456789291"})
        print(response.json())

        url = f"http://127.0.0.1:5000/api/v2.0/admin/hmac/add_user?username=admin&nonce={random.randint(0,2**32)}"
        data = {"username": "lady_killer12", "phone_number": "13456789291"}
        signature = hmac.new("admin".encode('utf-8'), json.dumps(data).encode('utf-8'), hashlib.sha256).hexdigest()
        print(signature)
        headers = {
            "Signature": signature
        }
        response = requests.post(url, headers=headers,
                                 json=data)
        print(response.json())

    def test_api_key_add_user(self):
        url = "http://127.0.0.1:5000/api/v2.0/admin/api_key/add_user"
        api_key = "wrong api key"
        headers = {
            "API-Key": api_key
        }
        response = requests.post(url, headers=headers,
                                 json={"username": "lady_killer9", "phone_number": "13456789291"})
        print(response.json())
        api_key = "d45056f8c7f512a7"
        headers = {
            "api_key": api_key
        }
        response = requests.post(url, headers=headers,
                                 json={"username": "lady_killer9", "phone_number": "13456789291"})
        print(response.json())


    def test_api_key_get_user_info(self):
        url = "http://192.168.10.2:5000/api/v2.0/api_key/get_user_info"
        api_key = "d45056f8c7f512a7"
        headers = {
            "API-Key": api_key
        }
        # 配置burpsuite為代理
        proxies = {
            "http":"http://192.168.142.128:8081"
        }
        response = requests.post(url,headers=headers,json={"username": "lady_killer9", "phone_number": "13456789291"},
                                 proxies=proxies,verify=False)
        print(response.status_code)
        print(response.json())


    def test_basic_auth(self):
        url = "http://127.0.0.1:5000/api/v2.0/admin/basic_auth/add_user"
        username = "admin"
        password = "wrong password"
        response = requests.post(url, auth=HTTPBasicAuth(username, password),
                                 json={"username": "lady_killer9", "phone_number": "13456789291"})
        print(response.json())
        username = "admin"
        password = "admin"
        response = requests.post(url, auth=HTTPBasicAuth(username, password),json={"username": "lady_killer9", "phone_number": "13456789291"})
        print(response.json())