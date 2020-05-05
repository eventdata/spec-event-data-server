import urllib

from pymongo import MongoClient

def __get_mongo_connection():
    # For local debugging
    MONGO_SERVER_IP = "172.29.100.22"
    MONGO_PORT = "3154"
    MONGO_USER = "event_reader"
    MONGO_PSWD = "dml2016"
    NUM_ARTICLES = 1000

    password = urllib.quote_plus(MONGO_PSWD)
    return MongoClient('mongodb://' + MONGO_USER + ':' + password + '@' + MONGO_SERVER_IP + ":" + MONGO_PORT)


db = __get_mongo_connection().event_scrape

event_doc_ids = set()

for entry in db.phoenix_events.find({}):
    event_doc_ids.add(entry["id"].split("_")[0])

print len(event_doc_ids)

print event_doc_ids

non_coded_doc_ids = []
limit = 10000
output_file = open("ids.txt", "w+")

for entry in db.stories.find({}):
    if str(entry["_id"]) not in event_doc_ids:
        non_coded_doc_ids.append(str(entry["_id"]))
        output_file.write(str(entry["_id"])+"\n")

        if limit > 0:
            limit -= 1
        else:
            break

output_file.close()









