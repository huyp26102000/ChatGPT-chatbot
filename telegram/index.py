from flask import Flask, request
import requests
import openai

PAGE_ACCESS_TOKEN = open(".messenger_token", "r").read()
openai.api_key = open(".gpt_api_key", "r").read()

app = Flask(__name__)
API = "https://graph.facebook.com/v16.0/me/messages?access_token="+PAGE_ACCESS_TOKEN


@app.route("/", methods=['GET'])
def fbverify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token")== "anystring":
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
        # print(type())
        request_body = {
            "recipient": {
                "id": sender_id
            },
            "message": {
                "text":completion['choices'][0]['message']['content']
            }
        }
        response = requests.post(API, json=request_body).json()
        return response

    except Exception as e:
        print(f"An error occurred: {e}")
        return "Error", 500
    return '200 OK HTTPS.'
if __name__ =='__main__':
    app.run()
