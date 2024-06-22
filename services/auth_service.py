import uuid
import base64
import traceback
import redis
import hashlib
import json
import hmac
import jwt

from functools import wraps
from flask import request,jsonify
from utils.log import log
from utils.mysql import MysqlCli
from setting import *

# 在这里实现验证用户名和密码的逻辑，通常是与存储的用户凭据进行比对
# 如果验证通过返回 True，否则返回 False
def check_basic_auth(username, password):
    try:
        cli = MysqlCli(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
        sql = f"select * from passwords where username = '{username}' limit 1"
        user = cli.select_one(sql)
        return (username, password) == (user['username'], user['password'])
    except Exception:
        log.logger.error(f"check_basic_auth failed,error:{traceback.format_exc()}")
        return False

def basic_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        resp = {
            "requestid": uuid.uuid4()
        }
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Basic '):
            resp['error'] = 'basic auth is required'
            log.logger.error(f"url:{request.url},resp:{resp}")
            return jsonify(resp), 400
        else:
            try:
                encoded_credentials = auth_header.split(' ')[1]
                decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
                username, password = decoded_credentials.split(':')
                if not check_basic_auth(username, password):
                    resp['error'] = 'basic auth failed,check your username or password is right'
                    log.logger.error(f"url:{request.url},resp:{resp}")
                    return jsonify(resp), 401
            except Exception:
                resp['error'] = f'basic auth failed,err: {traceback.format_exc()}'
                log.logger.error(f"url:{request.url},resp:{resp}")
                return jsonify(resp), 500

        return f(*args, **kwargs)

    return decorated_function


# 验证api_key是否存在
def check_api_key(api_key:str):
    try:
        cli = MysqlCli(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
        sql = f"select * from `keys` where `key` = '{api_key}' limit 1"
        key = cli.select_one(sql)
        if key:
            return True
        return False
    except Exception:
        log.logger.error(f"check_api_key failed,error:{traceback.format_exc()}")
        return False

def api_key_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        resp = {
            "requestid": uuid.uuid4()
        }
        # api key检查
        if "API-Key" not in request.headers:
            resp['error'] = 'API-Key is required in headers'
            log.logger.error(f"url:{request.url},resp:{resp}")
            return jsonify(resp), 400
        if not check_api_key(request.headers["API-Key"]):
            resp['error'] = f'api_key {request.headers["API-Key"]} is invalid'
            log.logger.error(f"url:{request.url},resp:{resp}")
            return jsonify(resp), 401
        return f(*args, **kwargs)

    return decorated_function

# 将字符串保存到Redis中，并设置过期时间
def save_nonce_with_expiry(key, value, expiry_seconds):
    """
    :param key: 键
    :param value: 值
    :param expiry_seconds: 过期时间（秒）
    """
    # 连接Redis数据库
    redis_client = redis.StrictRedis(host=REDIS_HOST,password=REDIS_PASSWORD, port=REDIS_PORT, db=REDIS_DB)
    redis_client.setex(key, expiry_seconds, value)

def check_nonce(key):
    """
    检查字符串是否存在于Redis中
    :param key: 键
    :return: 布尔值，表示键是否存在
    """
    # 连接Redis数据库
    redis_client = redis.StrictRedis(host=REDIS_HOST,password=REDIS_PASSWORD ,port=REDIS_PORT, db=REDIS_DB)
    return redis_client.exists(key)

# 校验username 返回密码
def check_username(username):
    try:
        cli = MysqlCli(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
        sql = f"select * from passwords where username = '{username}' limit 1"
        user = cli.select_one(sql)
        return user['password'] if user else ''
    except Exception:
        log.logger.error(f"check_basic_auth failed,error:{traceback.format_exc()}")
        return False

# 校验response
def check_response(response,realm,username,password,method,uri,req_nonce,nc,cnonce,qop):
    try:
        log.logger.info(f"check_response ,response:{response},realm:{realm},username:{username},"
                        f"password:{password},method:{method},uri:{uri},req_nonce:{req_nonce},nc:{nc},"
                        f"cnonce:{cnonce},qop:{qop}")
        # 校验nonce
        if not check_nonce(req_nonce):
            log.logger.error(f"check_signature failed,error:{req_nonce} not exist!")
            return False
        ha1=hashlib.md5(f"{username}:{realm}:{password}".encode()).hexdigest()
        ha2=hashlib.md5(f"{method}:{uri}".encode()).hexdigest()
        return response == hashlib.md5(f"{ha1}:{req_nonce}:{nc}:{cnonce}:{qop}:{ha2}".encode()).hexdigest()
    except Exception:
        log.logger.error(f"check_responce failed,error:{traceback.format_exc()}")
        return False


def digest_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        resp = {
            "requestid": uuid.uuid4()
        }
        # 生成随机数并返回401
        def request_401():
            resp['error'] = 'Unauthorized'
            nonce = str(uuid.uuid4())
            save_nonce_with_expiry(nonce, 1, 5 * 60)
            response = jsonify(resp)
            response.headers['WWW-Authenticate'] = f'Digest realm="Users", nonce="{nonce}", qop="auth"'
            return response, 401

        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return request_401()
            # 解析 Authorization 头部
            auth_data = auth_header[len('Digest '):]
            auth_fields = dict(field.strip().split('=', 1) for field in auth_data.replace('"', '').split(','))
            username = auth_fields.get('username')
            password = check_username(username)
            if not username:
                return request_401()
            if not password:
                resp['error'] = f'username{username} not found!'
                return jsonify(resp), 400
            method = request.method
            realm = auth_fields.get('realm')
            uri = auth_fields.get('uri')
            req_nonce = auth_fields.get('nonce')
            nc = auth_fields.get('nc')
            cnonce = auth_fields.get('cnonce')
            qop = auth_fields.get('qop')
            req_response = auth_fields.get('response')
            if not all([uri, req_nonce, nc, cnonce, qop, req_response]):
                return request_401()
            if not check_response(req_response, realm, username, password, method, uri, req_nonce, nc, cnonce, qop):
                resp['error'] = 'response is not right'
                return jsonify(resp), 400
        except Exception:
            resp['error'] = f'internal error,{traceback.format_exc()}'
            log.logger.error(f"url:{request.url},internal error,{traceback.format_exc()}")
            return jsonify(resp), 500
        return f(*args, **kwargs)

    return decorated_function

# 验证摘要
def check_signature(signture:str,username:str,nonce:int,data:dict):
    try:
        cli = MysqlCli(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
        sql = f"select * from `secrets` where `username` = '{username}' limit 1"
        secret = cli.select_one(sql)
        cli.close()
        if secret:
            server_signature = hmac.new(str(secret['secret']).encode('utf-8'), json.dumps(data).encode('utf-8'), hashlib.sha256).hexdigest()
            log.logger.info(f"secret:{str(secret['secret'])},data:{data},server_signature:{server_signature}")
            return  server_signature == signture
        log.logger.error(f"check_signature failed,error:{username} {secret}")
        return False
    except Exception:
        log.logger.error(f"check_signature failed,error:{traceback.format_exc()}")
        return False

def hmac_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        resp = {
            "requestid": uuid.uuid4()
        }
        # query检查 nonce username
        nonce = request.args.get('nonce', type=int)
        username = request.args.get('username')
        if nonce is None or username is None:
            resp['error'] = 'username or nonce not found in query string'
            log.logger.error(f"url:{request.url},resp:{resp}")
            return jsonify(resp)
        # 随机数验证
        if check_nonce(nonce):
            log.logger.error(f"check_signature failed,error:{nonce} is in database")
            resp['error'] = f"check_signature failed,error:{nonce} is in database"
            log.logger.error(f"url:{request.url},resp:{resp}")
            return jsonify(resp)
        save_nonce_with_expiry(nonce,1,MIN*60)
        # signature检查
        if "Signature" not in request.headers:
            resp['error'] = 'signature is required in headers'
            log.logger.error(f"url:{request.url},resp:{resp}")
            return jsonify(resp)
        # request是json
        if request.is_json:
            data = request.get_json()
            if not check_signature(request.headers['Signature'], username, nonce, data):
                resp['error'] = f'signature {request.headers["Signature"]} is invalid'
                log.logger.error(f"url:{request.url},resp:{resp}")
                return jsonify(resp),401
        else:
            resp['error'] = "Invalid JSON format in request"
            return jsonify(resp),400
        return f(*args, **kwargs)

    return decorated_function


def jwt_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        resp = {
            "requestid": uuid.uuid4()
        }
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            resp["message"] = "no Authorization header or invalid format"
            return jsonify(resp), 400
        try:
            token = auth_header.split(' ')[1]
            jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            resp["error"] = "token has expired"
            log.logger.error(f"url:{request.url},token:{token},resp:{resp}")
            return jsonify(resp), 401
        except jwt.InvalidTokenError:
            resp["message"] = f"invalid token {token}"
            log.logger.error(f"url:{request.url},token:{token},resp:{resp}")
            return jsonify(resp), 401
        except Exception as e:
            resp["message"] = f"interal error {e}"
            log.logger.error(f"url:{request.url},token:{token},resp:{resp}")
            return jsonify(resp), 500
        return f(*args, **kwargs)

    return decorated_function