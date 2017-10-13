import time
import json
import math
import time

from common import check_req_body_wrapper, regular_req_headers, _bad_request, oid_handler, \
    _unauthorized_body, pc, _no_user_named_xxx, check_header_wrapper, auth_wrapper
from database import db
from database import errors
from database import ReturnDocument
from flask_init import app
from flask_init import request
from setting import client_id, client_secret


@app.route('/api/v1/user', methods=['POST'])
@check_req_body_wrapper('password', 'nickname', 'phone', 'qq')
def register():
    try:
        json_req_data = json.loads(request.data)
        user_data = {
            'password': json_req_data['password'],
            'nickname': json_req_data['nickname'],
            'phone': json_req_data['phone'],
            'qq': json_req_data['qq'],
            'created_time': time.time(),
            'love_level': 0,
            'needs': []
        }
        # db['_users'].remove()
        if db['_users'].find_one({'phone': user_data['phone']}) is not None:
            return json.dumps(
                {'status': -1}), 200, regular_req_headers

        db['_users'].insert_one(user_data)

    except errors.DuplicateKeyError:
        return json.dumps({'status': 0}), 200, regular_req_headers
    except:
        return _bad_request, 400, regular_req_headers
    print(user_data)
    return json.dumps({'status': 1}), 200, regular_req_headers


@app.route('/api/v1/user/<phone>', methods=['POST'])
@check_req_body_wrapper('password', 'client_id', 'client_secret')
def login(phone):
    # 检查client_id, client_secret的正确性
    json_req_data = json.loads(request.data)
    if client_id == json_req_data['client_id'] and client_secret == json_req_data['client_secret']:
        pass
    else:
        return _unauthorized_body, 401, regular_req_headers

    # 检查通过，开始查询尝试登陆
    password = json_req_data['password']
    result = db['_users'].find_one({'phone': phone})
    if result is None:
        return json.dumps({'status': -1}), 200, regular_req_headers
    if password != result['password']:
        return json.dumps({'status': 0}), 200, regular_req_headers
    return json.dumps({'status': 1, 'token': pc.encrypt('%s %s %s' % (phone, str(math.floor(time.time())), client_id))}), 200, regular_req_headers


@app.route('/api/v1/user/<phone>', methods=['PUT'])
@check_header_wrapper('token')
@auth_wrapper
def edit_user(phone):
    new_data = json.loads(request.data)
    if '_id' in new_data or 'password' in new_data or 'create_time' in new_data:
        return json.dumps({'error': 'You can\'t change some param'}), 400, regular_req_headers

    result = db['_user'].find_one_and_update({'phone': phone}, {'$set': new_data},
                                              return_document=ReturnDocument.AFTER)
    return json.dumps({'status',1}), 200, regular_req_headers


@app.route('/api/v1/user/edit/<phone>', methods=['GET'])
@check_header_wrapper('token')
@auth_wrapper
def add_user_love_level(phone):
    result = db['_users'].find_one({'phone': phone})
    if result is None:
        return json.dumps({'error': 'no user find'}), 400, regular_req_headers
    love_level_previous = result['love_level']
    db['_users'].find_one_and_update(
        {'phone': phone}, {'$set': {'love_level': love_level_previous + 1}}, return_document=ReturnDocument.AFTER)
    result['love_level'] = love_level_previous + 1
    keys = list(filter(lambda key: key not in ['_id',
                                               'password', 'created_time'], result.keys()))
    values = list(map(lambda key: result[key], keys))
    return json.dumps(dict(zip(keys, values)), default=oid_handler), 200, regular_req_headers


@app.route('/api/v1/user/<phone>', methods=['GET'])
@check_header_wrapper('token')
@auth_wrapper
def get_user_info(phone):
    result = db['_users'].find_one({'phone': phone})
    if result is None:
        return json.dumps({'status': -1}), 200, regular_req_headers
    keys = list(filter(lambda key: key not in ['_id',
                                               'password', 'created_time'], result.keys()))
    values = list(map(lambda key: result[key], keys))
    return json.dumps(dict(zip(keys, values)), default=oid_handler), 200, regular_req_headers
