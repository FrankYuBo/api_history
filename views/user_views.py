import uuid
import traceback
import secrets

from flask import Flask, request, jsonify
from utils.mysql import MysqlCli
from utils.log import log
from utils.common import *
from services.auth_service import require_signature
from setting import *

app = Flask(__name__)
log.set_file()


# 管理员注册用户接口
@app.route('/api/v3.0/admin/add_user', methods=['POST'])
@require_signature
def add_user():
    resp = {
        "requestid": uuid.uuid4()
    }
    if request.is_json:
        data = request.get_json()
        username = data.get('username')
        if username is None:
            resp['error'] = 'username is required'
            log.logger.error(f"url:{request.url},params:{username},resp:{resp}")
            return jsonify(resp)
        phone_number = data.get('phone_number')
        if phone_number is None:
            resp['error'] = 'phone_number is required'
            log.logger.error(f"url:{request.url},params:{phone_number},resp:{resp}")
            return jsonify(resp)

        if not validate_username(username):
            resp['error'] = 'username length should not exceed 10'
            log.logger.error(f"url:{request.url},params:{username},resp:{resp}")
            return jsonify(resp)
        try:
            cli = MysqlCli(MYSQL_HOST,MYSQL_USER,MYSQL_PASSWORD,MYSQL_DATABASE)
            cli.insert_one("users",
                {
                    "username": username,
                    "phone_number": phone_number
                }
            )
            cli.close()
            secret = secrets.token_hex(16)
            cli.insert_one("secrets",
                           {
                               "username": username,
                               "secret": secret
                           })
            cli.close()
            resp['message'] = f'success to add user:{username},secretid:{username},secretkey:{secret},remember it!'
            log.logger.info(f"url:{request.url},params:{username},resp:{resp}")
        except Exception:
            log.logger.info(f"url:{request.url},params:{username},resp:{resp}")
            resp['error'] = f"failed to insert to mysql:{traceback.format_exc()}"
        return jsonify(resp)
    else:
        resp['error'] = "Invalid JSON format in request"
        return jsonify(resp)

# 用户获取信息接口
@app.route('/api/v3.0/get_user_info', methods=['POST'])
@require_signature
def get_user_info():
    resp = {
        "requestid": uuid.uuid4()
    }
    if request.is_json:
        data = request.get_json()
        username = data.get('username')
        if username is None:
            resp['error'] = 'username is required'
            log.logger.error(f"url:{request.url},params:{username},resp:{resp}")
            return jsonify(resp)

        if not validate_username(username):
            resp['error'] = 'username length should not exceed 10'
            log.logger.error(f"url:{request.url},params:{username},resp:{resp}")
            return jsonify(resp)
        try:
            cli = MysqlCli(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
            sql = f"select * from users where username = %s limit 1"
            user = cli.select_one(sql,params=(username,))
            phone_number = user['phone_number']
            user['phone_number'] = phone_number[:3] + '*' * (len(phone_number) - 7) + phone_number[-4:]
            resp['message'] = f'success to get user:{user}.'
            log.logger.info(f"url:{request.url},params:{username},resp:{resp}")
        except Exception:
            resp['error'] = f'failed to get user, error:{traceback.format_exc()}'
            log.logger.error(f"url:{request.url},params:{username},resp:{resp}")
        return jsonify(resp)
    else:
        resp['error'] = "Invalid JSON format in request"
        return jsonify(resp)