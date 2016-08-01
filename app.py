from flask import Flask
from flask import request, Response
from pymongo.mongo_client import MongoClient
from bson.json_util import dumps
from io import StringIO
import json
import sys
import urllib


app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS']=True

mongoClient = MongoClient()
api_key = 'CD75737EF4CAC292EE17B85AAE4B6'





def get_result(query):
    print "Inside Method"
    
    try:
        print query
        mongoClient = MongoClient()
        db = mongoClient.spec
       # query = '{"$or":[{"code":"030"},{"code":"111"}]}'
        print query
        dict = json.load(StringIO(unicode(query, 'utf-8')))
        print "Got Data"
        cursor = db.cameo_events.find(dict)
        print "Got Data"
        return '{"status": success, "data": '+dumps(cursor)+"}"
    except:
        e = sys.exc_info()[0]
        print e
        return '{"status": "error", "data":'+str(e)+"}"
    
@app.route("/api/data")
def get_data():
    query = request.args.get('query')
    print query
    response_data = ""
    api_key_received = request.args.get('api_key')
    if api_key_received == api_key:
        response_data = get_result(str(urllib.unquote_plus(query)))
    else:
        response_data = '{"status": "error", "data":"invalid api key"}"'
    return Response(response_data, mimetype='application/json')


if __name__ == "__main__":
    app.run(host='0.0.0.0')