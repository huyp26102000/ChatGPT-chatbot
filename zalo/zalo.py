import openai
import requests
class zalo:
    def __init__(self):
        pass
    def get_access_token(self):
        pass
    def send_message(self):
        pass

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