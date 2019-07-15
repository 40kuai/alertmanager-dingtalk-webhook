import os
import json
import requests

from flask import Flask
from flask import request

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def send():
    if request.method == 'POST':
        post_data = request.get_data()
        send_alert(string2dingding(bytes2json(post_data)))
        return 'success'
    else:
        return 'weclome to use prometheus alertmanager dingtalk webhook server!'


def bytes2json(data_bytes):
    data = data_bytes.decode('utf8').replace("'", '"')
    return json.loads(data)


def string2dingding(jsondata):
    alerts_dingding = """%s alert for %s\n[%s] %s\n""" % (len(jsondata["alerts"]),
                                                          ",".join(
                                                              ["%s=%s" % (key, jsondata["groupLabels"][key]) for key in
                                                               jsondata["groupLabels"]]),
                                                          len(jsondata["alerts"]),
                                                          jsondata["status"])

    for message in jsondata["alerts"]:
        alerts_dingding += """Labels\n%s\nAnnotations\n%s""" % (
        "\n".join(["%s=%s" % (key, message["labels"][key]) for key in message["labels"]]),
        "\n".join(["%s=%s" % (key, message["annotations"][key]) for key in message["annotations"]])
        )
    return alerts_dingding


def send_alert(data):
    token = os.getenv('ROBOT_TOKEN')
    if not token:
        print('you must set ROBOT_TOKEN env')
        return
    url = 'https://oapi.dingtalk.com/robot/send?access_token=%s' % token
    send_data = {
        "msgtype": "text",
        "text": {
            "content": data
        }
    }
    req = requests.post(url, json=send_data)
    result = req.json()
    if result['errcode'] != 0:
        print('notify dingtalk error: %s' % result['errcode'])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

