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

mongo_ip = "10.176.148.60"

mongoClient = MongoClient(host=mongo_ip)
api_key = 'CD75737EF4CAC292EE17B85AAE4B6'



project_dict = {'event_id': 1, 'date8': 1, 'year': 1, 'month': 1, 'day': 1,
                               'source': 1, 'src_actor': 1, 'src_agent': 1, 'src_other_agent': 1,
                               'target': 1, 'tgt_actor': 1, 'tgt_agent': 1, 'tgt_other_agent': 1,
                               'code': 1, 'root_code': 1, 'quad_class': 1, 'goldstein': 1,
                               'geoname': 1, 'country_code': 1, 'admin_info': 1, 'id': 1,  'url': 1,
                               'source_text': 1, 'longitude': 1, 'latitude': 1}

def create_project_dict(proj_str, delim=','):
    fields = proj_str.split(delim)
    proj_dict = {}
    for f in fields:
        proj_dict[f.strip()] = 1
    return proj_dict

def __get_mongo_connection():
    MONGO_PORT = "3154"
    MONGO_USER = "event_reader"
    MONGO_PSWD = "dml2016"
    MONGO_SERVER_IP = "172.29.100.14"
    MONGO_PORT = "3154"

    
    password = urllib.quote_plus(MONGO_PSWD)
    return MongoClient('mongodb://' + MONGO_USER + ':' + password + '@' + MONGO_SERVER_IP + ":" + MONGO_PORT)

def query_formatter(query_dict):
    for key in query_dict:
        if isinstance(query_dict[key], dict):
            query_formatter(query_dict[key])
        else:
            if str(query_dict[key]).startswith("$date"):
                date_str = str(query_dict[key]).replace("$date", "").replace("(", "").replace(")","").strip()
                date_obj = parser.parse(date_str)
                query_dict[key] = date_obj
                



def get_result(query, projection=None, unique=None):
    print "Inside Method"
    
    try:
        print query
        mongoClient = __get_mongo_connection()
        db = mongoClient.event_scrape
       
        print query
        query_dict = json.load(StringIO(unicode(query, 'utf-8')))
        print "Got Data"
        
        cursor = None
        query_formatter(query_dict)
        print query_dict
        if projection is not None:
            proj_dict = create_project_dict(projection)
            cursor = db.phoenix_events.find(query_dict, proj_dict)
        else:    
            cursor = db.phoenix_events.find(query_dict)
        print "Got Data"
        if unique is not None:
            cursor = cursor.distinct(unique)
        mongoClient.close()    
        return '{"status": "success", "data": '+dumps(cursor)+"}"
    except:
        e = sys.exc_info()[0]
        print e
        mongoClient.close()
        return '{"status": "error", "data":'+str(e)+"}"
    finally:
        mongoClient.close()
        
@app.route("/api/data")
def get_data():
    query = request.args.get('query')
    projection = request.args.get('select')
    unique = request.args.get('unique')
    print projection 
    print query
    print unique

    response_data = ""
    api_key_received = request.args.get('api_key')
    try:
        if api_key_received == api_key:
            response_data = get_result(str(urllib.unquote_plus(query)), projection, unique=unique)
        else:
            response_data = '{"status": "error", "data":"invalid api key"}"'
        resp = Response(response_data, mimetype='application/json')
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    except:
        e = sys.exc_info()[0]
        print e
        resp = Response('{"status": "error", "data":"'+str(e)+'"}')
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
        


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002)