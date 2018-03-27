
import requests
from requests.exceptions import ConnectionError

from time import sleep

request_url = "http://eventdata.utdallas.edu/api/fields?api_key=CD75737EF4CAC292EE17B85AAE4B6&datasource=cline_phoenix_fbis"

retry_interval = 60 #seconds
while True:
    try:
        sleep(retry_interval)
        resp = requests.get(request_url)
        retry_interval = 60


    except ConnectionError, e:
        print "Send E-mail Here"

        print e
        retry_interval = retry_interval * 2

