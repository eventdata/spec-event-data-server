from flask import Flask
from flask import request, Response
from pymongo.mongo_client import MongoClient
from bson.json_util import dumps
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
                'geoname': 1, 'country_code': 1, 'admin_info': 1, 'id': 1,  'url': 1,
                'source_text': 1, 'longitude': 1, 'latitude': 1}

# TODO: Uncomment when variable names change in MongoDB
# TODO: I'm not sure what event_id maps to. Leftover tags are {X, GID, None}. I set it to GID
# project_dict = {'GID': 1, 'Date': 1, 'Year': 1, 'Month': 1, 'Day': 1,
#                 'Source': 1, 'SrcActor': 1, 'SrcAgent': 1, 'SOthAgent': 1,
#                 'Target': 1, 'TgtActor': 1, 'TgtAgent': 1, 'TOthAgent': 1,
#                 'CAMEO': 1, 'RootCode': 1, 'QuadClass': 1, 'Goldstein': 1,
#                 'Geoname': 1, 'CountyCode': 1, 'AdminInfo': 1, 'ID': 1,  'URL': 1,
#                 'sourcetxt': 1, 'Lat': 1, 'Lon': 1}


def create_project_dict(proj_str, delim=','):
    fields = proj_str.split(delim)
    proj_dict = {}
    for f in fields:
        proj_dict[f.strip()] = 1
    return proj_dict


def create_group_dict(group_str, delim=','):
    groups = group_str.split(delim)
    group_dict = {}
    for entry in groups:
        group_dict[entry.strip()] = '$' + entry.strip()
    return group_dict


def query_formatter(query_dict):
    for key in query_dict:
        if isinstance(query_dict[key], dict):
            query_formatter(query_dict[key])
        else:
            if str(query_dict[key]).startswith("$date"):
                date_str = str(query_dict[key]).replace("$date", "").replace("(", "").replace(")", "").strip()
                date_obj = parser.parse(date_str)
                query_dict[key] = date_obj


def get_result(query, projection=None, unique=None, group=None):
    
    try:
        print("Processing: " + query)
        mongoClient = MongoClient(host=mongo_ip)
        db = mongoClient.spec
        query_dict = json.loads(query)

        query_formatter(query_dict)

        if unique and group:
            raise ValueError("'unique' and 'group' are not compatible.")

        if projection:
            proj_dict = create_project_dict(projection)
            cursor = db.phoenix_data.find(query_dict, proj_dict)
        elif group:
            proj_dict = create_project_dict(group)
            group_dict = create_group_dict(group)

            # Sort by order of elements in group
            sort_dict = {}
            for field in group_dict.keys():
                sort_dict["_id." + field] = 1

            cursor = db.phoenix_data.aggregate([{'$match': query_dict},
                                                {'$project': proj_dict},
                                                {'$group': {'_id': group_dict, 'total': {'$sum': 1}}},
                                                {'$sort': sort_dict}])
        else:
            cursor = db.phoenix_data.find(query_dict)

        if unique:
            cursor = cursor.distinct(unique)

        return '{"status": "success", "data": ' + dumps(cursor) + "}"

    except:
        e = sys.exc_info()[1]
        print(e)
        return '{"status": "error", "data":' + str(e) + "}"


@app.route("/api/data")
def get_data():
    query = request.args.get('query')
    projection = request.args.get('select')
    unique = request.args.get('unique')
    group = request.args.get('group')
    print(query)
    print(projection)
    print(unique)
    print(group)

    api_key_received = request.args.get('api_key')
    try:
        if api_key_received == api_key:
            response_data = get_result(str(urllib.unquote_plus(query)), projection, unique=unique, group=group)
        else:
            response_data = '{"status": "error", "data":"invalid api key"}"'
        resp = Response(response_data, mimetype='application/json')
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    except:
        e = sys.exc_info()[0]
        print(e)
        resp = Response('{"status": "error", "data":"'+str(e)+'"}')
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002)
