from flask import Flask
from flask import request, Response
from pymongo.mongo_client import MongoClient
from pymongo.errors import ConnectionFailure
from bson.json_util import dumps
from bson.json_util import ObjectId
import json
import sys
import urllib

reload(sys)
sys.setdefaultencoding('utf8')

from dateutil import parser

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

mongo_ip = "10.176.148.60"

api_key = 'CD75737EF4CAC292EE17B85AAE4B6'

ds_to_collection_names = {
     "cline_phoenix_nyt": "phoenix_nyt_events",
     "cline_phoenix_fbis": "phoenix_fbis_events",
     "cline_phoenix_swb" : "phoenix_swb_events",
     "icews":  "icews_events",
     "phoenix_rt": "phoenix_events"
}

ds_descrtions = {"cline_phoenix_nyt": "This data was produced using state-of-the-art PETRARCH-2 software to analyze content from the New York Times (1945-2005)",
                 "cline_phoenix_fbis": "This data was produced using state-of-the-art PETRARCH-2 software to analyze content from the the CIA's Foreign Broadcast Information Service (1995-2004).",
                 "cline_phoenix_swb" : "This data was produced using state-of-the-art PETRARCH-2 software to analyze content from the BBC Monitoring's Summary of World Broadcasts (1979-2015)",
                 "icews":  "Data produced for the Integrated Crisis Early Warning System (ICEWS) for the Defense Advanced Research Projects Agency (DARPA) and Office of Naval Research (ONR). Additional information about the ICEWS program can be found at http://www.icews.com/.",
                 "phoenix_rt": "Realtime event data in phoenix format genrated by system hosted at jetstream.org, TACC supported, from November 2017 onwards."}

projection_map = {}
fields_map = {}

def setup_app(app):
    mongoClient = __get_mongo_connection()

    db = mongoClient.event_scrape
    for key in ds_to_collection_names:
        entry = db[ds_to_collection_names[key]].find_one()
        fields = list(entry.keys())
        fields_map[key] = fields
        projection_map[key] = {}
        for field in fields:
            projection_map[key][field] = 1

    print "Initialization Complete."




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
    # For local debugging
    MONGO_SERVER_IP = "172.29.100.22"
    MONGO_PORT = "3154"
    MONGO_USER = "event_reader"
    MONGO_PSWD = "dml2016"
    NUM_ARTICLES = 1000

    password = urllib.quote_plus(MONGO_PSWD)
    return MongoClient('mongodb://' + MONGO_USER + ':' + password + '@' + MONGO_SERVER_IP + ":" + MONGO_PORT)


def get_result(dataset, query=None, aggregate=None, projection=None, unique=None):

    # Open connection
    try:
        mongoClient = __get_mongo_connection()
        db = mongoClient.event_scrape

        print db.collection_names()
        #print "Searching ", ds_to_collection_names[dataset]
        # Set the collection based on dataset
        collectionName = ds_to_collection_names[dataset]
        print collectionName
        # if collectionName == 'phoenix_events':
        #     print "Matched"
        # else:
        #     print "No Match"

        collection = db[collectionName]
        print "Collection Found"


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

            cursor = collection.find(query, proj_dict)

            if unique:
                cursor = cursor.distinct(unique)

        else:
            query_formatter(aggregate)
            cursor = collection.aggregate(aggregate)

        response = '{"status": "success", "data": ' + dumps(cursor) + "}"

    except:
        e = sys.exc_info()[1]
        print(e)
        response = '{"status": "error", "data":' + str(e) + "}"

    mongoClient.close()
    return response

def __verify_access(api_key_received):
    return api_key_received == api_key



@app.route("/api/datasources")
def get_datasources():
    api_key_received = request.args.get('api_key')


    try:
        if not __verify_access(api_key_received): raise ValueError("Invalid API Key")
        resp = Response('{"status": "success", "data": '+str(ds_to_collection_names.keys())+'}')
    except:
        e = sys.exc_info()
        print(e)
        resp = Response('{"status": "error", "data":"' + str(e) + '"}', mimetype='application/json')

    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route("/api/fields")
def get_datafields():
    api_key_received = request.args.get('api_key')
    data_source = request.args.get('datasource')

    try:
        if not __verify_access(api_key_received): raise ValueError("Invalid API Key")
        if data_source not in ds_to_collection_names: raise ValueError("Unknown datasource")
        resp = Response('{"status": "success", "data": '+str(fields_map[data_source])+'}')
    except:
        e = sys.exc_info()
        print(e)
        resp = Response('{"status": "error", "data":"' + str(e) + '"}', mimetype='application/json')

    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route("/api/describe")
def get_description():
    api_key_received = request.args.get('api_key')
    data_source = request.args.get('datasource')

    try:
        if not __verify_access(api_key_received): raise ValueError("Invalid API Key")
        if data_source not in ds_to_collection_names: raise ValueError("Unknown datasource")
        resp = Response('{"status": "success", "data": '+str(ds_descrtions[data_source])+'}')
    except:
        e = sys.exc_info()
        print(e)
        resp = Response('{"status": "error", "data":"' + str(e) + '"}', mimetype='application/json')

    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp



@app.route("/api/data")
def get_data():
    api_key_received = request.args.get('api_key')

    query = request.args.get('query')
    aggregate = request.args.get('aggregate')
    projection = request.args.get('select')
    unique = request.args.get('unique')
    group = request.args.get('group')
    dataset = request.args.get('dataset')

    try:
        if not __verify_access(api_key_received): raise ValueError("Invalid API key")

        if dataset is None:
            dataset = "phoenix_rt"

        assert(dataset in ds_to_collection_names)

        print("Dataset:    " + str(dataset))

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
            dataset,
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

setup_app(app)

if __name__ == "__main__":

    app.run(host='0.0.0.0', port=5002)