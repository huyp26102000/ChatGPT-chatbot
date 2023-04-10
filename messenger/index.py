import openai
import requests
from flask import Flask, request

PAGE_ACCESS_TOKEN = "EAAcFVgEEtY0BAA1YoUsjdjZC4Btzj30xq4UiUnv3W8LOtaIoZAp9B6uOJdLb21XpD1DZAFsOQSTJUcdgmWDFZACqUYfAaQ5UFBrYJQJPWmTKWk9AMu7drZAvRtRxqij2fbcQVEMId9MtydDh8wCyOZBn5GS0cant0YCt7HMWlbKyYMfoJYtYhB4EbOOBBj1yHnTZCBksUimD1OOqSuzM4oDxhPZAwhFi3ZAwZD"
openai.api_key = "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"
privacyPolicyRender = open("privacy-policy.html", "r").read()
termConditionRender = open("term-of-condition.html", "r", encoding="utf8").read()

app = Flask(__name__)
API = "https://graph.facebook.com/v16.0/me/messages?access_token=" + PAGE_ACCESS_TOKEN


@app.route("/", methods=['GET'])
def fbverify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == "anystring":
            return "Verification token missmatch", 403
        print(request.args['hub.challenge'], 200)
        return request.args['hub.challenge'], 200
    return "OK", 200


@app.route("/", methods=['POST'])
def fbwebhook():
    data = request.get_json()
    print(data)
    try:
        # Read messages from facebook messanger.
        message = data['entry'][0]['messaging'][0]['message']
        sender_id = data['entry'][0]['messaging'][0]['sender']['id']
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": message['text']},
            ]
        )
        request_body = {
            "recipient": {
                "id": sender_id
            },
            "message": {
                "text": completion['choices'][0]['message']['content']
            }
        }
        response = requests.post(API, json=request_body).json()
        return response

    except Exception as e:
        print(f"An error occurred: {e}")
        return "Error", 500
    return '200 OK HTTPS.'


@app.route("/term", methods=['GET'])
def get_html_term_of_condition():
    return termConditionRender


@app.route("/privacypolicy", methods=['GET'])
def get_html_privacypolicy():
    return privacyPolicyRender


if __name__ == '__main__':
    app.run()
