from flask import Flask, redirect
from flask import request, Response
from pymongo.mongo_client import MongoClient
from pymongo.errors import ConnectionFailure
#from bson.json_util import dumps
from bson.json_util import ObjectId
from bson import json_util
import json
from simplejson import dumps
import sys
import urllib
import os
from datetime import datetime
import requests
import atexit

from Test import locate_user
reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__, static_url_path='')
app.config['PROPAGATE_EXCEPTIONS'] = True


def exit_handler():
    print "Exiting from the server"

atexit.register(exit_handler)

def __get_mongo_connection():
    # For local debugging
    MONGO_SERVER_IP = "172.29.100.22"
    MONGO_PORT = "3154"
    MONGO_USER = "event_reader"
    MONGO_PSWD = "dml2016"
    NUM_ARTICLES = 1000

    password = urllib.quote_plus(MONGO_PSWD)
    return MongoClient('mongodb://' + MONGO_USER + ':' + password + '@' + MONGO_SERVER_IP + ":" + MONGO_PORT)
    #return MongoClient(host="127.0.0.1")

def create_html(json_list, keywords):
    pass


@app.route("/search/keyword")
def search_keyword():
    keywords = request.args.get('keywords')
    response_type = request.args.get('resp_type')
    if response_type is None:
        response_type = "json"
    if keywords is None:
        resp = Response("Bad Request, no keywords specified", mimetype='application/json')
    else:
        mongo_client = __get_mongo_connection()

        db = mongo_client.event_scrape

        result = list(db.stories.find({"$text":{"$search": " ".join(keywords.split(","))}}).limit(20))

        json_data = dumps(result, default=json_util.default)

        resp = Response(json_data, mimetype="application/json")

        return resp






if __name__ == "__main__":

    app.run(host='0.0.0.0', port=7002, threaded=True)
