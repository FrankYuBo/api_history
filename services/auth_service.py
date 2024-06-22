import hashlib
import uuid
import redis
import json

from functools import wraps
from flask import request, jsonify
from utils.log import log
from datetime import datetime,timedelta
from setting import *
from base64 import b64encode

log.set_file()


def verify_signature(signature, nonce,timestamp,algorithm,method,body_base64):
    format_str = f"{nonce}:{timestamp}:{algorithm}:{method}:{body_base64}"
    server_signature = hashlib.sha256(format_str.encode()).hexdigest()
    log.logger.info(format_str)
    log.logger.info(server_signature)
    return signature == server_signature


def require_signature(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        resp = {
            "requestid": uuid.uuid4()
        }
        secret_id = request.args.get('SecretId', type=str)
        nonce = request.args.get('Nonce', type=str)
        timestamp = request.args.get('Timestamp', type=int)
        algorithm = request.args.get('Algorithm', type=str)
        if secret_id is None:
            resp['error'] = 'No SecretId in query string'
            return jsonify(resp),400
        if nonce is None:
            resp['error'] = 'No Nonce in query string'
            return jsonify(resp),400
        if timestamp is None:
            resp['error'] = 'No Timestamp in query string'
            return jsonify(resp),400
        if algorithm is None:
            resp['error'] = 'No Algorithm in query string'
            return jsonify(resp),400
        if algorithm not in ["sha256"]:
            resp['error'] = f'can not support {algorithm}'
            return jsonify(resp), 400
        if (datetime.now() - timedelta(minutes=MIN)).timestamp() > timestamp:
            resp['error'] = 'Request is send before 5 mins ago, check Timestamp'
            return jsonify(resp), 400
        if ':' in nonce:
            resp['error'] = 'can not contain : in Nonce, generate a new one'
            return jsonify(resp), 400
        cli = redis.Redis.from_url(REDIS_URL)
        if cli.exists(nonce):
            resp['error'] = 'can not request with same Nonce'
            return jsonify(resp), 400
        else:
            cli.setex(nonce, MIN*60, 1)

        signature = request.headers.get('Signature')
        if not signature:
            resp['error'] = 'no Signature in headers'
            return jsonify(resp), 400

        # 解析 Authorization header，验证签名
        body_base64 = bytes.decode(b64encode(json.dumps(request.get_json(),ensure_ascii=False).encode()))
        if not verify_signature(signature, nonce,timestamp,algorithm,request.method,body_base64):
            resp['error'] = 'invalid signature'
            return jsonify(resp), 401

        return f(*args, **kwargs)

    return decorated_function
