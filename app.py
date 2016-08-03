from flask import Flask
from flask import request, Response
from pymongo.mongo_client import MongoClient
from bson.json_util import dumps
from io import StringIO
import json
import sys
import urllib

from dateutil import parser


app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS']=True

mongoClient = MongoClient()
api_key = 'CD75737EF4CAC292EE17B85AAE4B6'


project_dict = {
    "code": 1,
    "target": 1,
    "headline": 1,
    "country": 1,
    "coordinates": 1,
    "content": 1,
    "source": 1,
    "link": 1,
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

def query_formatter(query_dict):
    for key in query_dict:
        if isinstance(query_dict[key], dict):
            query_formatter(query_dict[key])
        else:
            if str(query_dict[key]).startswith("$date"):
                date_str = str(query_dict[key]).replace("$date", "").replace("(", "").replace(")","").strip()
                date_obj = parser.parse(date_str)
                query_dict[key] = date_obj
                



def get_result(query, projection=None):
    print "Inside Method"
    
    try:
        print query
        mongoClient = MongoClient()
        db = mongoClient.spec
       
        print query
        query_dict = json.load(StringIO(unicode(query, 'utf-8')))
        print "Got Data"
        
        cursor = None
        
        if projection is not None:
            proj_dict = create_project_dict(projection)
            cursor = db.cameo_events.find(query_dict, proj_dict)
        else:    
            cursor = db.cameo_events.find(query_dict)
        print "Got Data"
        return '{"status": "success", "data": '+dumps(cursor)+"}"
    except:
        e = sys.exc_info()[0]
        print e
        return '{"status": "error", "data":'+str(e)+"}"
    
@app.route("/api/data")
def get_data():
    query = request.args.get('query')
    projection = request.args.get('select')
    print projection 
    print query
    response_data = ""
    api_key_received = request.args.get('api_key')
    if api_key_received == api_key:
        response_data = get_result(str(urllib.unquote_plus(query)), projection)
    else:
        response_data = '{"status": "error", "data":"invalid api key"}"'
    return Response(response_data, mimetype='application/json')


if __name__ == "__main__":
    app.run(host='0.0.0.0')