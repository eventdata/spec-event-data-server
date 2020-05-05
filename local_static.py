import requests
from flask import Flask, Response, redirect
from flask import request, Response

app = Flask(__name__, static_url_path='')
app.config['PROPAGATE_EXCEPTIONS'] = True

@app.route("/")
def homepage():
    print("Inside Here")
    return redirect("/UTDEventData/", code=302)

#
# @app.route('/UTDEventData/<name>')
# def serve_static(name=""):
#     return _proxy(request)

@app.route('/UTDEventData/')
def serve_homepage():
    return _proxy(request)

@app.route('/UTDEventData/images')
def serve_css(name=""):
    return _proxy(request)


def _proxy(*args, **kwargs):
    resp = requests.request(
        method=request.method,
        url=request.url.replace(request.host_url, 'http://eventdata.utdallas.edu:4000/'),
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False)

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    response = Response(resp.content, resp.status_code, headers)
    return response


if __name__ == "__main__":

    app.run(host='0.0.0.0', port=5002, threaded=True)
