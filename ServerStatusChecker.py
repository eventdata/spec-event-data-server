
import requests
from requests.exceptions import ConnectionError
import subprocess as sp

from time import sleep

request_url = "http://eventdata.utdallas.edu/api/fields?api_key=CD75737EF4CAC292EE17B85AAE4B6&datasource=cline_phoenix_fbis"


def restart_server():
    sp.Popen("gnome-terminal -t web-server --working-directory=/home/ssalam/Desktop/spec-evet-data-server python app_v2.py", shell=True)

retry_interval = 60 #seconds
while True:
    try:
        sleep(retry_interval)
        resp = requests.get(request_url)
        retry_interval = 60


    except ConnectionError, e:
        print "Send E-mail Here"
        restart_server()
        print e
        retry_interval = retry_interval * 2

