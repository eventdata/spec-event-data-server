from flask import Flask
from flask import request, Response
from pymongo.mongo_client import MongoClient
from pymongo.errors import ConnectionFailure
from bson.json_util import dumps
from bson.json_util import ObjectId
import json
import sys
import urllib

from dateutil import parser

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

mongo_ip = "10.176.148.60"

api_key = 'CD75737EF4CAC292EE17B85AAE4B6'

project_dict = {'event_id': 1, 'date8': 1, 'year': 1, 'month': 1, 'day': 1,
                'source': 1, 'src_actor': 1, 'src_agent': 1, 'src_other_agent': 1,
                'target': 1, 'tgt_actor': 1, 'tgt_agent': 1, 'tgt_other_agent': 1,
                'code': 1, 'root_code': 1, 'quad_class': 1, 'goldstein': 1,
                'geoname': 1, 'country_code': 1, 'admin_info': 1, 'id': 1, 'url': 1,
                'source_text': 1, 'longitude': 1, 'latitude': 1}

def create_project_dict(proj_str, delim=','):

    # If no projection, don't build the dict
    if not proj_str: return

    fields = proj_str.split(delim)
    proj_dict = {}

    # Don't return _id by default, but can be overridden
    proj_dict['_id'] = 0

    for f in fields:
        proj_dict[f.strip()] = 1

    return proj_dict


def create_group_dict(group_str, delim=','):
    groups = group_str.split(delim)
    group_dict = {}
    for entry in groups:
        group_dict[entry.strip()] = '$' + entry.strip()
    return group_dict


def query_formatter(query):
    # Aggregation formatting
    if type(query) is list:
        for stage in query:
            query_formatter(stage)
        return

    print(query)
    # Query formatting
    for key in query:
        if type(query[key]) is dict:
            # Convert strict oid tags into ObjectIds to allow id comparisons
            if 'oid' in query[key]:
                query[key] = ObjectId(query[key]['oid'])
            else:
                query_formatter(query[key])

        else:
            if str(query[key]).startswith("$date"):
                date_str = str(query[key]).replace("$date", "").replace("(", "").replace(")", "").strip()
                date_obj = parser.parse(date_str)
                query[key] = date_obj

def __get_mongo_connection():
    MONGO_PORT = "3154"
    MONGO_USER = "event_reader"
    MONGO_PSWD = "dml2016"
    MONGO_SERVER_IP = "172.29.100.14"
    MONGO_PORT = "3154"


    password = urllib.quote_plus(MONGO_PSWD)
    return MongoClient('mongodb://' + MONGO_USER + ':' + password + '@' + MONGO_SERVER_IP + ":" + MONGO_PORT)
    # For local debugging
    # return MongoClient("127.0.0.1:27017")


def get_result(query=None, aggregate=None, projection=None, unique=None):

    # Open connection
    try:
        mongoClient = __get_mongo_connection()
        db = mongoClient.event_scrape
    except ConnectionFailure:
        e = sys.exc_info()[1]
        print(e)
        return '{"status": "error", "data": "could not connect to database"}'

    # Query submission
    try:
        if query is not None and aggregate:
            raise ValueError("'query' and 'aggregate' are not compatible")

        if query is None and not aggregate:
            raise ValueError("'query' or 'aggregate' must be given")

        if query is not None:
            query_formatter(query)
            print(query)
            proj_dict = create_project_dict(projection)

            cursor = db.phoenix_events.find(query, proj_dict)

            if unique:
                cursor = cursor.distinct(unique)

        else:
            query_formatter(aggregate)
            cursor = db.phoenix_events.aggregate(aggregate)

        response = '{"status": "success", "data": ' + dumps(cursor) + "}"

    except:
        e = sys.exc_info()[1]
        print(e)
        response = '{"status": "error", "data":' + str(e) + "}"

    mongoClient.close()
    return response


@app.route("/api/data")
def get_data():
    api_key_received = request.args.get('api_key')

    query = request.args.get('query')
    aggregate = request.args.get('aggregate')
    projection = request.args.get('select')
    unique = request.args.get('unique')
    group = request.args.get('group')

    try:
        if api_key_received != api_key: raise ValueError("Invalid API key")

        if query:
            query = json.loads(urllib.unquote_plus(query))
            print("Query:      " + str(query))

        if aggregate:
            aggregate = json.loads(urllib.unquote_plus(aggregate))
            print("Aggregate:  " + str(aggregate))

        # Grouping overrides aggregate
        if group:
            proj_dict = create_project_dict(group)
            group_dict = create_group_dict(group)

            # Sort by order of elements in group
            sort_dict = {}
            for field in group_dict.keys():
                sort_dict["_id." + field] = 1

            # Convert the query into an aggregation
            aggregate = [{'$match': query},
                         {'$project': proj_dict},
                         {'$group': {'_id': group_dict, 'total': {'$sum': 1}}},
                         {'$sort': sort_dict}]
            query = None

            print("Grouping:   " + str(aggregate))

        if projection: print("Projection: " + str(projection))
        if unique: print("Unique:     " + str(unique))

        response_data = get_result(
            query=query,
            aggregate=aggregate,
            projection=projection,
            unique=unique
        )

        resp = Response(response_data, mimetype='application/json')

    except:
        e = sys.exc_info()
        print(e)
        resp = Response('{"status": "error", "data":"' + str(e) + '"}', mimetype='application/json')

    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002)