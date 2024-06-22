import re
import string
import traceback
import secrets
import hmac
import hashlib
import json
import uuid
import redis

from utils.mysql import MysqlCli
from setting import *
from utils.log import log

log.set_file()

# 生成密码
def generate_random_password(length):
    characters = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password


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


# 生成nonce
def gen_nonce():
    try:
        cli = MysqlCli(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
        cli.insert_one("nonces",{
            "nonce":uuid.uuid4()
        })
    except Exception:
        log.logger.error(f"check_signature failed,error:{traceback.format_exc()}")
        return False



