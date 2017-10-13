import json
import bson
import time

from flask_init import app
from flask_init import request

from database import db
from database import errors
from database import ReturnDocument
from database import DESCENDING

from common import _bad_request
from common import _no_user_named_xxx
from common import regular_req_headers

from common import auth_wrapper
from common import check_req_body_wrapper
from common import check_header_wrapper
from setting import waiting
from setting import finished
from common import oid_handler


@app.route('/api/v1/needs', methods=['POST'])
@check_header_wrapper('token')
@auth_wrapper
@check_req_body_wrapper('creator_phone', 'desc', 'continue_time', 'sex', 'longitude', 'latitude',
                        'location', 'destination')
def add_need(phone):
    json_req_data = json.loads(request.data)
    try:
        keys = ['creator_phone', 'desc', 'continue_time', 'sex', 'longitude', 'latitude',
                'location',
                'destination']
        values = map(lambda key: json_req_data[key], keys)
        data_to_insert = dict(zip(keys, values))
        data_to_insert['create_time'] = int(time.time())
        data_to_insert['status'] = waiting
        data_to_insert['helper_phone'] = ''
        insert_id = db['_needs'].insert_one(data_to_insert).inserted_id
        print(insert_id)
        result = db['_users'].find_one_and_update({'phone': json_req_data['creator_phone']}, {
            '$push': {
                'needs': {
                    '$each': [insert_id]
                }
            }
        }, return_document=ReturnDocument.AFTER)
        if result is None:
            return _no_user_named_xxx, 400, regular_req_headers
        return json.dumps(data_to_insert, default=oid_handler), 200, regular_req_headers
    except:
        return _bad_request, 400, regular_req_headers


@app.route('/api/v1/needs/<id>', methods=['GET'])
@check_header_wrapper('token')
@auth_wrapper
def get_needs_info(phone, id):
    result = db['_needs'].find_one({'_id': bson.ObjectId(id)})
    if result is None:
        return json.dumps({'error': 'no such need found'}), 400, regular_req_headers
    keys = list(filter(lambda key: key not in ['_id'], result.keys()))
    values = list(map(lambda key: result[key], keys))
    return json.dumps(dict(zip(keys, values)), default=oid_handler), 200, regular_req_headers


@app.route('/api/v1/needs/<id>', methods=['PUT'])
@check_header_wrapper('token')
@auth_wrapper
def edit_need(phone, id):
    new_data = json.loads(request.data)
    if '_id' in new_data or 'creator_id' in new_data or 'create_time' in new_data:
        return json.dumps({'error': 'You can\'t change some param'}), 400, regular_req_headers

    result = db['_needs'].find_one_and_update({'_id': bson.ObjectId(id)}, {'$set': new_data},
                                              return_document=ReturnDocument.AFTER)
    return json.dumps(result, default=oid_handler), 200, regular_req_headers


@app.route('/api/v1/needs/<id>', methods=['DELETE'])
@check_header_wrapper('token')
@auth_wrapper
def delete_need(phone, id):
    result = db['_needs'].find_one({'_id': bson.ObjectId(id)})
    if result is None:
        return json.dumps({'error': 'no such need found'}), 400, regular_req_headers
    db['_users'].update_many({'needs': {
        '$in': [bson.ObjectId(id)]
    }}, {
        '$pull': {
            'needs': {
                '$in': [bson.ObjectId(id)]
            }
        }
    })
    db['_needs'].delete_one({'_id': bson.ObjectId(id)})

    return json.dumps({'msg': 'delete successfully!'}), 200, regular_req_headers


@app.route('/api/v1/needs', methods=['GET'])
@check_header_wrapper('token')
@auth_wrapper
def get_all_nest(phone):
    # db['_needs'].remove()
    results = db['_needs'].find()
    temp = dict()
    temp['need'] = []
    for value in results:
        temp['need'].append(value)
    return json.dumps(temp, default=oid_handler), 200, regular_req_headers

# @app.route('/api/v1/needs/help',methods=[''])
