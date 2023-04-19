import openai
import requests
import json
from datetime import datetime
class zalo:
    def __init__(self):
        pass
    def get_access_token(self):
        pass
    def send_message(self, accesstoken, sender_id, message, trush, data, ask_gpt):
        if ask_gpt:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": message},
                ]
            )
            message = completion['choices'][0]['message']['content']
        msg = {
            "recipient": {
                "user_id": sender_id
            },
            "message": {
                # "text": completion['choices'][0]['message']['content'],
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
        header = {
            'access_token': accesstoken
        }
        response = requests.post('https://openapi.zalo.me/v2.0/oa/message', headers=header, json=msg)
        if response.status_code == 200:
            if trush == True:
                with open(".message_id.txt", "a+", encoding='utf-8') as f:
                    datamsgid = str(data["message"]["msg_id"])
                    datamsgtext = str(data["message"]["text"])
                    f.writelines("\n" + datamsgid + ": " + datamsgtext)
        else:
            print('Lỗi khi gửi tin nhắn: ', response.content)
    def get_msg_from_gpt(self, api, msg):
        openai.api_key = api
        prompt = msg

        res = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=100,
            temperature=0
        )
        return res.choices[0].text

    def defaultInfo(self):
        openai.api_key = "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"
        info = open(".default_info.txt", 'r', encoding='utf-8').read()
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": info},
            ]
        )
        # return completion['choices'][0]['message']['content']