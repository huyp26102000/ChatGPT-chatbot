import json, zalo as gpt
import openai
import requests
from flask import Flask, request
from hashlib import sha256
from base64 import urlsafe_b64encode
from datetime import datetime

appconfig = open("config.json", "r").read()
appconfig = json.loads(appconfig)
openai.api_key = appconfig["gpt_api_key"]

app = Flask(__name__)
question = ['', 'MOTIVATION QUOTE', 'RÚT NGẮN ĐOẠN VĂN', 'TƯ VẤN VÀ TRÒ CHUYỆN']
@app.route("/", methods=['GET'])
def zaloverify():
    print('code_verifier:', appconfig['code_verifier'])
    code_verifier = appconfig['code_verifier']
    code_verifier_bytes = code_verifier.encode('ascii')
    code_challenge_bytes = sha256(code_verifier_bytes).digest()
    code_challenge = urlsafe_b64encode(code_challenge_bytes).decode('ascii').rstrip('=')
    print('code_challenge:', code_challenge)
    return "OK", 200

def get_access_token_from_code(app_id, secret_key, code):
    url = "https://oauth.zaloapp.com/v4/oa/access_token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "secret_key": secret_key
    }
    data = {
        "app_id": app_id,
        "code": code,
        "grant_type": "authorization_code"
    }

    response = requests.post(url, headers=headers, data=data).json()

    return response

def refresh_access_token(app_id, secret_key, refresh_access_token):
    url = 'https://oauth.zaloapp.com/v4/oa/access_token'
    data = {
        'app_id': app_id,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_access_token
    }
    headers = {
        'secret_key': secret_key,
    }
    response = requests.post(url, headers=headers, data=data)

    if response.ok:
        access_token = response.json()['access_token']
        print('New access token:', access_token)

        # update new access token to config.json
        with open('config.json', 'r') as f:
            data = json.load(f)
        data['access_token'] = access_token
        data['refresh_access_token'] = response.json()['refresh_token']
        with open('config.json', 'w') as f:
            json.dump(data, f)
    else:
        print('Failed to refresh access token:', response.content)

    return response

def get_zalo_access_token():
    with open('config.json', 'r') as f:
        config = json.load(f)

    # Check if access token is still valid
    expires_in = 0
    access_token = config['access_token']
    if access_token:
        token_expiry = datetime.fromtimestamp(float(config['expires_in']))
        expires_in = (token_expiry - datetime.now()).total_seconds()
    if expires_in > 0:
        return access_token

    # Access token is expired, refresh it
    refresh_token = config['refresh_access_token']
    try:
        if refresh_token:
            new_token_response = refresh_access_token(config['app_id'], config['secret_key'], refresh_token)
            if new_token_response.ok:
                new_token_data = new_token_response.json()
                access_token = new_token_data['access_token']
                if access_token:
                    config['access_token'] = access_token
                    config['expires_in'] = str(datetime.now().timestamp() + float(new_token_data['expires_in']))
                    config['refresh_access_token'] = new_token_data['refresh_token']
                    with open('config.json', 'w') as f:
                        json.dump(config, f)
                    return access_token
                else:
                    print('Failed to get access token from refresh token response:', new_token_data)
            else:
                print('Failed to refresh access token:', new_token_response.content)
        else:
            print('No refresh token found in config file.')

    except Exception as ex:
        print("error: ", ex)

    return ''

def send_message(access_token, sender_id, message, should_store, message_data, use_gpt):
    message = 'Bạn hãy đóng vai một nhân viên chăm sóc học sinh của trường cao đẳng Viễn đông và trả lời câu hỏi: ' + message
    if use_gpt:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": message},
            ]
        )
        message = completion['choices'][0]['message']['content']

    payload = {
        "recipient": {
            "user_id": sender_id
        },
        "message": {
            "text": message,
            "attachment": {
                "type": "template",
                "payload": {
                    "buttons": [
                        {
                            "title": "Rút ngắn đoạn văn",
                            "type": "oa.query.show",
                            "payload": "RÚT NGẮN ĐOẠN VĂN"
                        },
                        {
                            "title": "Motivation quote",
                            "type": "oa.query.show",
                            "payload": "MOTIVATION QUOTE"
                        },
                        {
                            "title": "TƯ VẤN VÀ TRÒ CHUYỆN",
                            "type": "oa.query.show",
                            "payload": "TƯ VẤN VÀ TRÒ CHUYỆN"
                        },
                    ]
                }
            }
        }
    }

    headers = {
        'access_token': access_token
    }

    response = requests.post('https://openapi.zalo.me/v2.0/oa/message', headers=headers, json=payload)

    if response.ok:
        if should_store:
            with open(".message_id.txt", "a+", encoding='utf-8') as f:
                message_id = str(message_data["message"]["msg_id"])
                message_text = str(message_data["message"]["text"])
                f.writelines("\n" + message_id + ": " + message_text)
    else:
        print('Lỗi khi gửi tin nhắn: ', response.content)
@app.route("/", methods=['POST'])
def zalowebhook():
    data = request.get_json()
    print(data)
    trush = True
    ask_gpt = True
    access_token = get_zalo_access_token()
    # print(access_token)
    # getAT = get_access_token_from_code(appconfig['app_id'], appconfig['secret_key'], appconfig['code'])
    # at = appconfig["access_token"]
    # error = "error_name"
    # if error in getAT:
    #     value = getAT[error]
    #     print('Tồn tại khóa: %s trong khi yêu cầu lấy Access Token mới, giá trị là: %s' % (error, value))
    # else:
    #     print(getAT["access_token"])
    #     at = getAT["access_token"]


    if(data['sender']['id'] == '4356460878800442485'):#check id of Tien Nguyen
        # send default information
        gpt3 = gpt.zalo()

        try:
            # gpt3.defaultInfo()
            message = data['message']['text']
            sender_id = data['sender']['id']

            if data['message']['text'] == "RÚT NGẮN ĐOẠN VĂN":
                message = "Vui lòng nhập đoạn văn cần rút gọn"
                ask_gpt = False
                send_message(access_token, sender_id, message, trush, data, ask_gpt)
                return '200 OK HTTPS.', 200

            elif data['message']['text'] == "MOTIVATION QUOTE":
                ask_gpt = True
                message = "Đưa cho tôi một câu nói truyền cảm hứng cho hôm nay"
                send_message(access_token, sender_id, message, trush, data, ask_gpt)
                return '200 OK HTTPS.', 200

            for quest in question:
                if (data['message']['text'] == quest):
                    # request to send message here
                    trush = False

            messages = open(".message_id.txt", "r", encoding='utf-8').read()

            msg = messages.split("\n")
            for items in msg:
                item = items.split(": ")
                if data["message"]["msg_id"] == item[0] or data["message"]["text"] == item[1]:
                    print(item)
                    return '400 BAD REQUEST.', 400

            print(message)
            if data['event_name'] == 'user_send_text':
                send_message(access_token, sender_id, message, trush, data, ask_gpt)

        except Exception as e:
            print(f"An error occurred: {e}")
            return "Error", 500
    else:
        print(data['sender']['id'])
    return '200 OK HTTPS.', 200

if __name__ == '__main__':
    app.run()
