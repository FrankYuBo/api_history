import jwt

from flask import Flask, request, jsonify
from services.auth_service import basic_auth,api_key_auth,digest_auth,hmac_auth,jwt_auth
from utils.common import *
from setting import *
from datetime import datetime,timedelta
app = Flask(__name__)
log.set_file()

# 添加用户 用于添加用户时无需额外增加用户关联的密钥等信息时的接口
def add_user():
    resp = {
        "requestid": uuid.uuid4()
    }
    log.logger.info(request.headers)

    # request是json
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
            cli = MysqlCli(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
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

# 获取用户信息，用于各种认证的获取用户信息接口
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
            return jsonify(resp),400

        if not validate_username(username):
            resp['error'] = 'username length should not exceed 10'
            log.logger.error(f"url:{request.url},params:{username},resp:{resp}")
            return jsonify(resp),400
        try:
            cli = MysqlCli(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
            sql = f"select * from users where username = '{username}' limit 1"
            user = cli.select_all(sql)
            resp['message'] = f'success to get user:{user}.'
            log.logger.info(f"url:{request.url},params:{username},resp:{resp}")
        except Exception:
            resp['error'] = f'failed to get user, error:{traceback.format_exc()}'
            log.logger.error(f"url:{request.url},params:{username},resp:{resp}")
            return jsonify(resp),500
        return jsonify(resp)
    else:
        resp['error'] = "Invalid JSON format in request"
        return jsonify(resp),40

# 用户登录获取jwt token接口
@app.route('/api/v2.0/admin/jwt/login', methods=['POST'])
def get_jwt_token():
    resp = {
        "requestid": uuid.uuid4()
    }
    if request.is_json:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        if username is None or password is None:
            resp['error'] = 'username or password is required'
            log.logger.error(f"url:{request.url},params:{username},resp:{resp}")
            return jsonify(resp),400

        if not validate_username(username):
            resp['error'] = 'username length should not exceed 10'
            log.logger.error(f"url:{request.url},params:{username},resp:{resp}")
            return jsonify(resp),400
        try:
            cli = MysqlCli(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
            sql = f"select * from passwords where username = '{username}' limit 1"
            user = cli.select_one(sql)
            if not user:
                resp['error'] = 'username not found'
                log.logger.error(f"url:{request.url},params:{username},resp:{resp}")
                return jsonify(resp), 400
            if user['password'] != password:
                resp['error'] = 'password is not right'
                log.logger.error(f"url:{request.url},params:{username},resp:{resp}")
                return jsonify(resp), 401
            payload = {
                "iss": "lady_killer9",
                "exp": datetime.now() + timedelta(seconds=5*60),
                "jti": str(uuid.uuid4())
            }
            resp['message'] = f'success to login :{user},token:{jwt.encode(payload,JWT_SECRET,algorithm="HS256")}'
            log.logger.info(f"url:{request.url},params:{username},resp:{resp}")
            return jsonify(resp), 200
        except Exception:
            resp['error'] = f'failed to get user, error:{traceback.format_exc()}'
            log.logger.error(f"url:{request.url},params:{username},resp:{resp}")
            return jsonify(resp),500
    else:
        resp['error'] = "Invalid JSON format in request"
        return jsonify(resp),400

# 管理员注册用户接口 v2.0增加jwt sha256算法
@app.route('/api/v2.0/admin/jwt/add_user', methods=['POST'])
@jwt_auth
def add_user_jwt():
    return add_user()

# 用户获取信息接口 v2.0 增加jwt sha256算法
@app.route('/api/v2.0/jwt/get_user_info', methods=['POST'])
@jwt_auth
def get_user_info_jwt():
    return get_user_info()

# 管理员注册用户接口 v2.0增加hmac sha256算法
@app.route('/api/v2.0/admin/hmac/add_user', methods=['POST'])
@hmac_auth
def add_user_hmac():
    resp = {
        "requestid": uuid.uuid4()
    }
    # request是json
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
            secret = secrets.token_hex(16)
            cli.insert_one("secrets",
                           {
                               "username": username,
                               "secret": secret
                           })
            cli.close()
            resp['message'] =f'success to add user:{username},secret {secret},remember it!'
            log.logger.info(f"url:{request.url},params:{username},resp:{resp}")
        except Exception:
            log.logger.info(f"url:{request.url},params:{username},resp:{resp}")
            resp['error'] = f"failed to insert to mysql:{traceback.format_exc()}"
        return jsonify(resp)
    else:
        resp['error'] = "Invalid JSON format in request"
        return jsonify(resp)

# 用户获取信息接口 v2.0 增加hmac
@app.route('/api/v2.0/hmac/get_user_info', methods=['POST'])
@hmac_auth
def get_user_info_hmac():
    return get_user_info()

# 管理员注册用户接口 v2.0增加digest算法
@app.route('/api/v2.0/admin/digest_auth/add_user', methods=['POST'])
@digest_auth
def add_user_digest():
    return add_user()

# 用户获取信息接口 v2.0增加digest算法
@app.route('/api/v2.0/digest_auth/get_user_info', methods=['POST'])
@digest_auth
def get_user_info_digest_auth():
    return get_user_info()

# 管理员注册用户接口 v2.0 增加api token
@app.route('/api/v2.0/admin/api_key/add_user', methods=['POST'])
@api_key_auth
def add_user_api_key():
    resp = {
        "requestid": uuid.uuid4()
    }
    # request是json
    if request.is_json:
        data = request.get_json()
        username = data.get('username')
        if username is None:
            resp['error'] = 'username is required'
            log.logger.error(f"url:{request.url},params:{username},resp:{resp}")
            return jsonify(resp),400
        phone_number = data.get('phone_number')
        if phone_number is None:
            resp['error'] = 'phone_number is required'
            log.logger.error(f"url:{request.url},params:{phone_number},resp:{resp}")
            return jsonify(resp),400
        if not validate_username(username):
            resp['error'] = 'username length should not exceed 10'
            log.logger.error(f"url:{request.url},params:{username},resp:{resp}")
            return jsonify(resp),400
        try:
            cli = MysqlCli(MYSQL_HOST,MYSQL_USER,MYSQL_PASSWORD,MYSQL_DATABASE)
            cli.insert_one("users",
                {
                    "username": username,
                    "phone_number": phone_number
                }
            )
            key = secrets.token_hex(16)
            cli.insert_one("keys",
                           {
                               "username": username,
                               "key": key
                           })
            cli.close()
            resp['message'] =f'success to add user:{username},key {key},remember it!'
            log.logger.info(f"url:{request.url},params:{username},resp:{resp}")
        except Exception:
            log.logger.info(f"url:{request.url},params:{username},resp:{resp}")
            resp['error'] = f"failed to insert to mysql:{traceback.format_exc()}"
            return jsonify(resp),500
        return jsonify(resp)
    else:
        resp['error'] = "Invalid JSON format in request"
        return jsonify(resp),400


# 用户获取信息接口 v2.0 增加api token
@app.route('/api/v2.0/api_key/get_user_info', methods=['POST'])
@api_key_auth
def get_user_info_api_key():
    return get_user_info()

# 管理员注册用户接口 v2.0 增加密码
@app.route('/api/v2.0/admin/basic_auth/add_user', methods=['POST'])
@basic_auth
def add_user_basic_auth():
    resp = {
        "requestid": uuid.uuid4()
    }
    # 请求是json格式
    if request.is_json:
        data = request.get_json()
        username = data.get('username')
        # username检查
        if username is None:
            resp['error'] = 'username is required'
            log.logger.error(f"url:{request.url},params:{username},resp:{resp}")
            return jsonify(resp),400
        if not validate_username(username):
            resp['error'] = 'username length should not exceed 10'
            log.logger.error(f"url:{request.url},params:{username},resp:{resp}")
            return jsonify(resp),400
        # phone_number检查
        phone_number = data.get('phone_number')
        if phone_number is None:
            resp['error'] = 'phone_number is required'
            log.logger.error(f"url:{request.url},params:{phone_number},resp:{resp}")
            return jsonify(resp),400
        # 插入数据库
        try:
            cli = MysqlCli(MYSQL_HOST,MYSQL_USER,MYSQL_PASSWORD,MYSQL_DATABASE)
            cli.insert_one("users",
                {
                    "username": username,
                    "phone_number": phone_number
                }
            )
            pwd = generate_random_password(secrets.choice(range(8, 17)))
            cli.insert_one("passwords", {
                "username": username,
                "password": pwd
            })
            cli.close()
            resp['message'] = f'success to add user:{username},password {pwd},remember it!'
            log.logger.info(f"url:{request.url},params:{username},resp:{resp}")
        # 异常返回
        except Exception:
            log.logger.info(f"url:{request.url},params:{username},resp:{resp}")
            resp['error'] = f"failed to insert to mysql:{traceback.format_exc()}",500
            return jsonify(resp)
        return jsonify(resp)
    # 请求不是json格式
    else:
        resp['error'] = "Invalid JSON format in request"
        return jsonify(resp),400

# 用户获取信息接口 v2.0 增加密码
@app.route('/api/v2.0/basic_auth/get_user_info', methods=['POST'])
@basic_auth
def get_user_info_basic_auth():
    return get_user_info()