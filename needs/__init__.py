import json
import bson
import datetime
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
from common import oid_handler


@app.route('/api/v1/needs', methods=['POST'])
@check_req_body_wrapper('creator_id', 'desc', 'continue_time', 'sex', 'longitude', 'latitude',
                        'location',
                        'destination')
def add_need():
    json_req_data = json.loads(request.data)
    try:
        keys = ['creator_id', 'desc', 'continue_time', 'sex', 'longitude', 'latitude', 'location',
                'destination']
        values = map(lambda key: json_req_data[key], keys)
        data_to_insert = dict(zip(keys, values))
        data_to_insert['create_time'] = int(time.time())
        data_to_insert['status'] = waiting
        data_to_insert['helper_id'] = -1
        insert_id = db['_needs'].insert_one(data_to_insert).inserted_id
        print(insert_id)
        result = db['_users'].find_one_and_update({'_id': json_req_data['creator_id']}, {
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
def get_needs_info(id):
    result = db['_needs'].find_one({'_id': bson.ObjectId(id)})
    if result is None:
        return json.dumps({'error': 'no such need found'}), 400, regular_req_headers
    keys = list(filter(lambda key: key not in ['_id'], result.keys()))
    values = list(map(lambda key: result[key], keys))
    return json.dumps(dict(zip(keys, values)), default=oid_handler), 200, regular_req_headers


@app.route('/api/v1/needs/<id>', methods=['PUT', 'POST'])
def edit_need(id):
    new_data = json.loads(request.data)
    if '_id' in new_data or 'creator_id' in new_data or 'create_time' in new_data:
        return json.dumps({'error': 'You can\'t change some param'}), 400, regular_req_headers

    result = db['_needs'].find_one_and_update({'_id': bson.ObjectId(id)}, {'$set': new_data},
                                              return_document=ReturnDocument.AFTER)
    return json.dumps(result, default=oid_handler), 200, regular_req_headers
