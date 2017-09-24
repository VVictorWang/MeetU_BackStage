import json
from binascii import b2a_hex, a2b_hex
from functools import wraps

from Crypto.Cipher import AES

from flask_init import request

import datetime
import math
import bson

from setting import client_id


def oid_handler(x):
    if isinstance(x, datetime.datetime):
        return math.floor(x.timestamp())
    elif isinstance(x, bson.ObjectId):
        return str(x)
    else:
        raise TypeError(x)


class Crypt():
    def __init__(self, key):
        self.key = key
        self.mode = AES.MODE_CBC

    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        length = 16
        count = len(text)
        add = length - (count % length)
        self.ciphertext = cryptor.encrypt(text)
        return str(b2a_hex(self.ciphertext), 'utf-8')

    # 解密后，去掉补足的空格用strip() 去掉
    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        plain_text = str(cryptor.decrypt(a2b_hex(text)), 'utf-8')
        return plain_text.rstrip('\0')


pc = Crypt('hzylovelyl1314ab')

# 初始化常见数据的类
_unauthorized_body = json.dumps({'error': 'Permission Denied!'})

_bad_request = json.dumps({'error': 'Your request is invalid!'})

_no_user_named_xxx = json.dumps({'error': 'No user matched!'})

regular_req_headers = {'content-type': 'application/json'}


# 检查是否包含给定的头
def check_headers(headers, *headers_key):
    for key in headers_key:
        if headers.get(key.lower()) != None:
            continue
        else:
            return False
    return True


# 根据请求头进行认证的函数

def auth_wrapper(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if 'username' in kwargs:
            username = kwargs['username']
        else:
            username = None

        try:
            authorization = request.headers.get('authorization')
            decoded_auth = pc.decrypt(authorization)

            keys = ['username', 'timestamp', 'client_id']
            values = decoded_auth.split(' ')
            _dict = dict(zip(keys, values))
            if username != None and _dict['username'] != username:
                return _unauthorized_body, 401, regular_req_headers
            else:
                if int(_dict['timestamp']) - math.floor(datetime.time.time()) >= 3600 * 24 * 30:
                    return _unauthorized_body, 401, regular_req_headers
                else:
                    if _dict['client_id'] == client_id:
                        pass
                    else:
                        return _unauthorized_body, 401, regular_req_headers
        except:
            return _bad_request, 400, regular_req_headers

        # auth pass!
        if 'username' in kwargs:
            return fn(*args, **kwargs)
        else:
            return fn(*args, **kwargs, username=_dict['username'])

    return wrapped


def check_header_wrapper(*headers):
    def dec(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            # check if headers have key provided
            if not check_headers(request.headers, *headers):
                return _bad_request, 400, regular_req_headers
            return fn(*args, **kwargs)

        return wrapped

    return dec


def check_req_body_wrapper(*keys):
    def dec(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            # check if headers have key provided
            try:
                decoded_req_data = json.loads(request.data)

                # 检查需要的key是否都在
                results = sum(map(lambda key: key in decoded_req_data, keys)) == len(list(keys))
                if results:
                    return fn(*args, **kwargs)
                else:
                    return _bad_request, 400, regular_req_headers
            except:
                return _bad_request, 400, regular_req_headers

        return wrapped

    return dec
