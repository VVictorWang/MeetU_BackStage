from pymongo import MongoClient
from pymongo import DESCENDING
from pymongo import ASCENDING
from pymongo import errors
from pymongo import ReturnDocument

client = MongoClient('localhost', 27017)

db = client['MeetU']
