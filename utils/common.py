import re

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