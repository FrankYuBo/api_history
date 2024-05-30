import uuid
import re
import traceback

from flask import Flask, request, jsonify
from mysql import MysqlCli
from log import log
from setting import *

app = Flask(__name__)
log.set_file()

# 验证username
def validate_username(username:str)->bool:
    if len(username) > 20:
        return False
    return True

# 验证手机号
def validate_phone_number(phone_number:str)->bool:
    # 使用正则表达式检查手机号格式
    pattern = re.compile(r'^1[3456789]\d{9}$')
    if re.match(pattern, phone_number):
        return True
    else:
        return False

# 管理员注册用户接口
@app.route('/api/v1.0/admin/add_user', methods=['POST'])
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
            resp['message'] = f'success to add user:{username}!'
            log.logger.info(f"url:{request.url},params:{username},resp:{resp}")
        except Exception:
            log.logger.info(f"url:{request.url},params:{username},resp:{resp}")
            resp['error'] = f"failed to insert to mysql:{traceback.format_exc()}"
        return jsonify(resp)
    else:
        resp['error'] = "Invalid JSON format in request"
        return jsonify(resp)

# 用户获取信息接口
@app.route('/api/v1.0/get_user_info', methods=['POST'])
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
            sql = f"select * from users where username = '{username}' limit 1"
            user = cli.select_all(sql)
            resp['message'] = f'success to get user:{user}.'
            log.logger.info(f"url:{request.url},params:{username},resp:{resp}")
        except Exception:
            resp['error'] = f'failed to get user, error:{traceback.format_exc()}'
            log.logger.error(f"url:{request.url},params:{username},resp:{resp}")
        return jsonify(resp)
    else:
        resp['error'] = "Invalid JSON format in request"
        return jsonify(resp)


if __name__ == '__main__':
    app.run()
