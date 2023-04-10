import json, zalo as gpt

import openai
import requests
from flask import Flask, request
from hashlib import sha256
from base64 import urlsafe_b64encode, urlsafe_b64decode

appconfig = open("config.json", "r").read()
appconfig = json.loads(appconfig)
# privacyPolicyRender = open("privacy-policy.html", "r").read()
# termConditionRender = open("term-of-condition.html", "r", encoding="utf8").read()
app = Flask(__name__)
question = ['Motivation quote', 'Rút ngắn đoạn văn', 'Thông tin tuyển sinh']

@app.route("/", methods=['GET'])
def zaloverify():
    print('code_verifier:', appconfig['code_verifier'])
    code_verifier = appconfig['code_verifier']
    code_verifier_bytes = code_verifier.encode('ascii')
    code_challenge_bytes = sha256(code_verifier_bytes).digest()
    code_challenge = urlsafe_b64encode(code_challenge_bytes).decode('ascii').rstrip('=')
    print('code_challenge:', code_challenge)
    return "OK", 200


@app.route("/", methods=['POST'])
def zalowebhook():
    data = request.get_json()
    print(data)
    URLAccessToken = "https://oauth.zaloapp.com/v4/oa/access_token"
    secret_key = appconfig['secret_key']
    header = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'secret_key': secret_key
    }
    body = {
        "app_id":appconfig["app_id"],
        "code": appconfig["code"],
        "grant_type": "authorization_code"
    }

    getAT = requests.post(URLAccessToken, headers=header, data=body).json()
    if(getAT['error_name'] == "Authorized code expired"):
        pass
    if(data['event_name'] == 'user_received_message'):
        print('received')
        return '200 OK HTTPS.', 200

    # if(data['sender']['id'] == '4356460878800442485'):
    try:
        message = data['message']['text']
        sender_id = data['sender']['id']
        for quest in question:
            if (message == quest):
                # request to send message here
                # response = requests.post('https://openapi.zalo.me/v2.0/oa/message', json='body').json()
                return '200 OK HTTPS.', 200

        gpt3 = gpt.zalo()
        msg = {
            "recipient": {
                "user_id": sender_id
            },
            "message": {
                "text": gpt3.get_msg_from_gpt(appconfig['gpt_api_key'], message),
                # "text": message,
                "attachment": {
                    "type": "template",
                    "payload": {
                        "buttons": [
                            {
                                "title": "Rút ngắn đoạn văn",
                                "type": "oa.query.show",
                                "payload": "Rút ngắn đoạn văn"
                            },
                            {
                                "title": "Motivation quote",
                                "type": "oa.query.hide",
                                "payload": "Motivation quote"
                            },
                            {
                                "title": "Thông tin tuyển sinh",
                                "type": "oa.query.show",
                                "payload": "Thông tin tuyển sinh"
                            },
                        ]
                    }
                }
            }
        }
        header = {
            'access_token': appconfig["access_token"]
        }
        response = requests.post('https://openapi.zalo.me/v2.0/oa/message', headers=header, json=msg)
        if response.status_code == 200:
            pass
        else:
            print('Lỗi khi gửi tin nhắn: ', response.content)

    except Exception as e:
        print(f"An error occurred: {e}")
        return "Error", 500
    # else:
    #     print('none')
    return '200 OK HTTPS.', 200

if __name__ == '__main__':
    app.run()
