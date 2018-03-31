import json
import requests


url = "http://eventdata.utdallas.edu:5002/api/data?api_key=EmNc8Pbp5XEUIuzlIdxqVlP5g6S1KlNe&query={'date8':{'$gt':'20180320', '$lt': '20180328'}}"

response = requests.get(url)

print response

events = json.loads(response.content)

print "Data Loading Complete. Entry count ", len(events)

document_to_event_map = {}

for event in events:

    doc_id = event['id'].split("_")[0]
    if doc_id not in document_to_event_map:
        document_to_event_map[doc_id] = []

    document_to_event_map[doc_id].append(event)


print len(document_to_event_map)

count_map = {}

for doc in document_to_event_map:
    if len(document_to_event_map[doc]) not in count_map:
        count_map[len(document_to_event_map[doc])] = 0
    count_map[len(document_to_event_map[doc])] += 1


print count_map







