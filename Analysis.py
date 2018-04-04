import json
import requests


url = "http://eventdata.utdallas.edu/api/data?api_key=EmNc8Pbp5XEUIuzlIdxqVlP5g6S1KlNe&query={\"date8\":{\"$gt\":\"20180228\", \"$lt\": \"20180401\"}}"

response = requests.get(url)

print response

data = json.loads(response.content)

#print response.content

print "Data Loading Complete. Entry count ", len(data["data"])

document_to_event_map = {}

for event in data['data']:

    doc_id = event["id"].split("_")[0]
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

root_code_match = 0
root_code_not_found = 0
event_match = 0
doc_count = 0

for doc_id in document_to_event_map:
    if len(document_to_event_map[doc_id]) == 2:
        events = document_to_event_map[doc_id]
        #print events[0]
        if 'source' not in events[0] or 'target' not in events[0]:
            continue

        if 'source' not in events[1] or 'target' not in events[1]:
            continue
        if events[0]['source'] == events[1]['source']:

            if events[0]['target'] == events[1]['target']:
                root_code_match += 1
                if events[0]['code'] == events[1]['code']:
                    event_match += 1
                    print "Event Match"
                    doc_id = events[0]['id'].split("_")[0]
                    print doc_id
                    url = "http://eventdata.utdallas.edu/api/article?api_key=EmNc8Pbp5XEUIuzlIdxqVlP5g6S1KlNe&doc_id="+doc_id

                    response = requests.get(url)

                    print response.content

                    data = json.loads(response.content)
                    sentences = data['data']
                    sent1_id = events[0]['id'].split("_")[1]
                    sent2_id = events[1]['id'].split("_")[1]
                    sent1 = ""
                    sent2 = ""
                    for sentence in sentences:
                        if sentence["sentence_id"] == sent1_id:
                            sent1 = sentence["sentence"]
                        if sentence["sentence_id"] == sent2_id:
                            sent2 = sentence["sentence"]
                    print sent1_id, ":", sent1
                    print sent2_id, ":", sent2
                    print events[0]['source'], events[0]['target'], events[0]['code']



        doc_count += 1

print doc_count
print root_code_match
print event_match









