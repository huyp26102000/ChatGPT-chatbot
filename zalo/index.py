import openai
import requests
from flask import Flask, request
from hashlib import sha256
from base64 import urlsafe_b64encode, urlsafe_b64decode

code_verifier = open("code_verifier", "r").read()
# privacyPolicyRender = open("privacy-policy.html", "r").read()
# termConditionRender = open("term-of-condition.html", "r", encoding="utf8").read()
app = Flask(__name__)

@app.route("/", methods=['GET'])
def zaloverify():
    print('code_verifier:', code_verifier)
    code_verifier_bytes = code_verifier.encode('ascii')
    code_challenge_bytes = sha256(code_verifier_bytes).digest()
    code_challenge = urlsafe_b64encode(code_challenge_bytes).decode('ascii').rstrip('=')
    print('code_challenge:', code_challenge)
    return "OK", 200


@app.route("/", methods=['POST'])
def zalowebhook():
    data = request.get_json()
    print(data)
    try:
        message = data['message']['text']
        if(message=='xin chao'):
            # request to send message here
            response = requests.post('entry', json='body').json()
            return response
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Error", 500
    return '200 OK HTTPS.'


# @app.route("/term", methods=['GET'])
# def get_html_term_of_condition():
#     return termConditionRender
#
#
# @app.route("/privacypolicy", methods=['GET'])
# def get_html_privacypolicy():
#     return privacyPolicyRender


if __name__ == '__main__':
    app.run()
