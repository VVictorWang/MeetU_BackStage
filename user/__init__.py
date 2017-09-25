import datetime
import json
import math
import time

from common import check_req_body_wrapper, regular_req_headers, _bad_request, oid_handler, \
    _unauthorized_body, pc, _no_user_named_xxx, check_header_wrapper, auth_wrapper
from database import db
from database import errors
from flask_init import app
from flask_init import request
from setting import client_id, client_secret


@app.route('/api/v1/user', methods=['POST'])
@check_req_body_wrapper('username', 'password', 'sex', 'age')
def register():
    try:
        json_req_data = json.loads(request.data)
        user_data = {'username': json_req_data['username'],
                     'password': json_req_data['password'],
                     'created_time': datetime.datetime.utcnow(),
                     'sex': json_req_data['sex'],
                     'age': json_req_data['age']
                     }
        db['_users'].insert_one(user_data)
    except errors.DuplicateKeyError:
        return json.dumps({'error': 'Username already exists!'}), 400, regular_req_headers
    except:
        return _bad_request, 400, regular_req_headers
    print(user_data)
    return json.dumps(user_data, default=oid_handler), 200, regular_req_headers


@app.route('/api/v1/<username>/login', methods=['POST'])
@check_req_body_wrapper('password', 'clientid', 'client_secret')
def login(username):
    # 检查client_id, client_secret的正确性
    json_req_data = json.loads(request.data)
    if client_id == json_req_data['client_id'] and client_secret == json_req_data['client_secret']:
        pass
    else:
        return _unauthorized_body, 401, regular_req_headers

    # 检查通过，开始查询尝试登陆
    password = json_req_data['password']
    result = db['_users'].find_one({'username': username, 'password': password})
    if result != None:
        return json.dumps({
            'msg': 'Logged in successfully!',
            'Authorization': pc.encrypt(
                '%s %s %s' % (username, str(math.floor(time.time())), client_id))
        }), 200, regular_req_headers
    else:
        return _no_user_named_xxx, 400, regular_req_headers


@app.route('/api/v1/user/<username>/info', methods=['GET'])
@check_header_wrapper('authorization')
@auth_wrapper
def get_user_info(username):
    # auth pass

    # query user info
    result = db['_users'].find_one({'username': username})
    if result == None:
        return _no_user_named_xxx, 400, regular_req_headers

    # generate response
    keys = list(filter(lambda key: key not in ['_id', 'password', 'created_time'], result.keys()))
    values = list(map(lambda key: result[key], keys))
    return json.dumps(dict(zip(keys, values)), default=oid_handler), 200, regular_req_headers
