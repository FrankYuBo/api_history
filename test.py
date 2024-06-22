# --coding utf-8--
import unittest
import requests
import uuid
import json
import hashlib
import base64
from utils.mysql import MysqlCli
from setting import *
from datetime import datetime

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

    def test_db(self):

        cli = MysqlCli(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
        sql = f"select * from users where username = %s limit 1"
        username= 'lady_kill8'
        user = cli.select_one(sql, params=(username,))
        print(user)

    # 测试get_user_info api
    def test_get_user_info(self):
        nonce = str(uuid.uuid4())
        timestamp = datetime.now().timestamp()
        algorithm='sha256'
        method = 'POST'
        url = f"http://192.168.10.2:5000/api/v3.0/get_user_info?SecretId=admin&Nonce={nonce}&Timestamp={int(timestamp)}&Algorithm={algorithm}"
        body = {
            "username": "l' or 1=1--"
        }
        body_base64 = bytes.decode(base64.b64encode(json.dumps(body,ensure_ascii=False).encode()))
        format_str  =f"{nonce}:{int(timestamp)}:{algorithm}:{method}:{body_base64}"
        print(format_str)

        signature = hashlib.sha256(format_str.encode()).hexdigest()

        print(signature)
        headers = {
            'Signature': signature
        }
        # 配置burpsuite為代理
        proxies = {
            "http":"http://192.168.142.128:8081"
        }
        # 发送请求
        resp = requests.post(url,json=body,headers=headers,proxies=proxies,verify=False)
        print(resp.json())