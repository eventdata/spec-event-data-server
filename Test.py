from pymongo.mongo_client import MongoClient
from io import StringIO
from bson.json_util import dumps
import json

mongoClient = MongoClient()

db = mongoClient.spec


query = '{"$or":[{"code":"030"},{"code":"111"}]}'

dict = json.load(StringIO(unicode(query, 'utf-8')))

cursor = db.cameo_events.find(dict)

data = dumps(cursor)

print data