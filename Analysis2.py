import json
import requests
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

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
output_file = open("events.txt", "w+")

similar_count = {}
with open("output.txt", "w+") as out:
    for doc_id in document_to_event_map:
        if len(document_to_event_map[doc_id]) == 3:
            events = document_to_event_map[doc_id]
            #print events[0]
            if 'source' not in events[0] or 'target' not in events[0]:
                continue

            if 'source' not in events[1] or 'target' not in events[1]:
                continue

            if 'source' not in events[2] or 'target' not in events[2]:
                continue

            url = "http://eventdata.utdallas.edu/api/article?api_key=EmNc8Pbp5XEUIuzlIdxqVlP5g6S1KlNe&doc_id=" + doc_id

            response = requests.get(url)

            data = json.loads(response.content)
            sentences = data['data']

            for i in range(0, len(events)):
                print >> out, events[i]['code'], events[i]['source'], events[i]['target']
                sent_id = events[i]['id'].split("_")[1]
                j = 0
                while sent_id != str(sentences[j]['sentence_id']):
                    j += 1
                print >> out, sent_id, ": ", sentences[j]["sentence"]

            from newsplease import NewsPlease

            print >> out, "================= FULL ARTICLE ==============="
            article = NewsPlease.from_url(events[0]['url'])
            print >> out, events[0]['url']
            print >> out, article.text

            doc_count += 1
out.close()
print doc_count
print root_code_match
print event_match

print similar_count









