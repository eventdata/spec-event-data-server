from pymongo.mongo_client import MongoClient
import random

mongo_ip = "10.176.148.60"

mongoClient = MongoClient(host=mongo_ip)


db = mongoClient.spec

stories = db['phoenix_data']

cs = db['pd_concise']

for story in stories.find():
    print "T"
    if random.randrange(10) == 1:
        cs.insert(story)
    


