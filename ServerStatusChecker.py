
import requests
from requests.exceptions import ConnectionError
import subprocess as sp
import os
from time import sleep

request_url = "http://eventdata.utdallas.edu/api/fields?api_key=CD75737EF4CAC292EE17B85AAE4B6&datasource=cline_phoenix_fbis"


def restart_server():
    #sp.Popen("gnome-terminal", shell=True, env=dict(os.environ, DISPLAY=":0.0", XAUTHORITY="/home/ssalam/.Xauthority"))
    os.system("gnome-terminal -x python app_v2.py")
retry_interval = 60 #seconds
restart_server()
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

