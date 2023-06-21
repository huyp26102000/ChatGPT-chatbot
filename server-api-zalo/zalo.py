import openai
import requests
import json
from datetime import datetime, timedelta
class zalo:
    def __init__(self):
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

from pymongo import MongoClient
connectionString = "mongodb://localhost:27017/chatbot-gpt"
client = MongoClient(connectionString)

db = client['Chatbot-chatgpt']
thread_collection = db['thread']
message_collection = db['messages']
# def check_entry_message():
#     message_id = '123'
#
#     message = message_collection.find_one({'message_id': message_id})
#     if message is None:
#         # Create a new document if not found
#         new_message = {'message_id': message_id, 'data': []}
#         message_collection.insert_one(new_message)
#         print('save')
#         return None
#     return message
# def add_action(sender_id, thread, action):
#     if thread is not None:
#         now = datetime.now()
#         find_thread_user = thread_collection.find_one({'sender_id': sender_id})
#         if find_thread_user is not None:
#             thread['actions'] = action
#             thread['created_at'] = now
#
#         thread_collection.replace_one({'_id': thread['_id']}, thread, upsert=True)
# def get_recent_thread(sender_id):
#     now = datetime.now()
#     five_minutes_ago = now - timedelta(minutes=5)
#     print(five_minutes_ago)
#     thread = thread_collection.find_one({'sender_id': sender_id, "created_at": {"$gte": five_minutes_ago, "$lte": now}})
#     if thread is None:
#         # Create a new document if not found
#         thread = {'sender_id': sender_id, 'created_at': datetime.now(), 'actions': 'None'}
#         thread_collection.insert_one(thread)
#         return None
#     else:
#         return thread

# id = '4356460878800442485'
# thread = get_recent_thread(id)
# print(thread)
# add_action(id, thread, 'Short poem')
# db.messages.delete_many({})
# db.thread.delete_many({})
# mes = "Trường cao đẳng viễn đông có phòng tự học không?" + " dịch sang tiếng việt"
# data = {"question" : mes}
# response = requests.post('http://localhost:3000/api/chat', json=data).json()
#
# print(response['text'])