from pymongo.mongo_client import MongoClient
from io import StringIO
from bson.json_util import dumps
import json
import ast
import yaml
from datetime import datetime

from dateutil import parser

date_format = "%m-%d-%Y %I:%M:%S %p"

project_dict = {
    "code": 1,
    "target": 1,
    "headline": 0,
    "country": 0,
    "coordinates": 0,
    "content": 0,
    "source": 1,
    "link": 0,
    "location": 1,
    "date": 1,
    "_id": 1    
}

def create_project_dict(proj_str, delim=','):
    fields = proj_str.split(delim)
    proj_dict = {}
    for f in fields:
        proj_dict[f.strip()] = 1
    return proj_dict
  
create_project_dict('hello,world,dhaka')    

def query_formatter(query_dict):
    for key in query_dict:
        if isinstance(query_dict[key], dict):
            query_formatter(query_dict[key])
        else:
            if str(query_dict[key]).startswith("$date"):
                date_str = str(query_dict[key]).replace("$date", "").replace("(", "").replace(")","").strip()
                date_obj = parser.parse(date_str)
                query_dict[key] = date_obj
                

mongoClient = MongoClient(host="dmlhdpc10")
 
db = mongoClient.spec
 
query = '{"date" : { "$gte" : "$date(06-17-2016)" }}'
 
 
  
query_dict = json.load(StringIO(unicode(query, 'utf-8')))
 
query_formatter(query_dict=query_dict)
   
print query_dict
 
cursor = db.cameo_events.find(query_dict, create_project_dict('source, target, code, date'))
 
data = dumps(cursor)
 
print data

print datetime.fromtimestamp(1465999427000/1000.0)

