import json

import openai
import requests
from flask import Flask, request
from hashlib import sha256
from base64 import urlsafe_b64encode
from datetime import datetime, timedelta
from pymongo import MongoClient

appconfig = open("config.json", "r").read()
appconfig = json.loads(appconfig)
openai.api_key = appconfig["gpt_api_key"]

connectionString = "mongodb://localhost:27017/chatbot-gpt"
client = MongoClient(connectionString)

dbs = client.list_database_names()
db = client['Chatbot-chatgpt']
connection = db.list_collection_names()
thread_collection = db['thread']
message_collection = db['messages']

app = Flask(__name__)
question = ['MOTIVATION QUOTE', 'RÚT NGẮN ĐOẠN VĂN', 'TƯ VẤN VÀ TRÒ CHUYỆN']
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
        times = datetime.fromtimestamp(float(expires_in))
        formatted_time = times.strftime("%I:%M %p")
        print("Expiration time: ", formatted_time)
        return access_token

    # Access token is expired, refresh it
    refresh_token = config['refresh_access_token']
    try:
        if refresh_token:
            new_token_response = refresh_access_token(config['app_id'], config['secret_key'], refresh_token)
            if new_token_response.ok:
                new_token_data = new_token_response.json()
                access_token = new_token_data['access_token']
                print('Access Token is expired.\nNew access token: ', access_token)
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

def get_recent_thread(sender_id):
    now = datetime.now()
    five_minutes_ago = now - timedelta(minutes=15)
    thread = thread_collection.find_one({'sender_id': sender_id, "created_at": {"$gte": five_minutes_ago, "$lte": now}})
    if thread is None:
        # Create a new document if not found
        thread = {'sender_id': sender_id, 'created_at': datetime.now(), 'actions': 'None'}
        thread_collection.insert_one(thread)
        return thread
    else:
        return thread

def check_entry_message(message_data):
    if message_data['event_name'] == 'user_click_chatnow':
        return None
    else:
        message_id = message_data['message']['msg_id']

    message = message_collection.find_one({'message_id': message_id})
    if message is not None:
        return message
    # Create a new document if not found
    new_message = {'message_id': message_id, 'data': message_data}
    message_collection.insert_one(new_message)
    return None
def add_action(sender_id, thread, action):
    now = datetime.now()
    if thread is not None:
        find_thread_sender = thread_collection.find_one({'sender_id': sender_id})
        if find_thread_sender is not None:
            thread['actions'] = action
            thread['created_at'] = now

        thread_collection.replace_one({'_id': thread['_id']}, thread, upsert=True)
    else:
        thread = {'sender_id': sender_id, 'created_at': now, 'actions': 'None'}
        thread_collection.insert_one(thread)
def load_buttons(title_button):
    pay_load = {'buttons': []}
    if len(title_button) > 5:
        return 'Không hỗ trợ nhiều hơn 5 button'
    for i in title_button:
        for key, values in i.items():
            pay_load['buttons'] += {
                "title": key,
                "type": "oa.query.show",
                "payload": values
            },
    return pay_load
def options_button(opt):
    button_payload = {'buttons': []}
    if opt == 0:
        button_items = [
            {
                "Kết thúc": "Kết thúc"
            },
        ]
        button_payload = load_buttons(button_items)
    elif opt == 1:
        button_items = [
            {
                "Rút ngắn đoạn văn": "Rút ngắn đoạn văn"
            },
            {
                "Motivation quotes": "Motivation Quotes"
            },
            {
                "TƯ VẤN VÀ TRÒ CHUYỆN": "Tư vấn và trò chuyện"
            },
        ]
        button_payload = load_buttons(button_items)
    elif opt == 2:
        button_items = [
            {
                "Chat với GPT": "Chat với GPT"
            },
            {
                "Chat với tư vấn viên": "Chat với tư vấn viên"
            },
            {
                "Hỏi về thông tin trường": "Hỏi về thông tin trường"
            },
        ]
        button_payload = load_buttons(button_items)
    elif opt == 3:
        button_items = [
            {
                "Bạn là Phụ Huynh": "Phụ Huynh"
            },
            {
                "Bạn là Học Sinh/Sinh Viên": "Học Sinh/Sinh Viên"
            },
        ]
        button_payload = load_buttons(button_items)
    return button_payload
def message_gpt(message):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": message},
        ]
    )
    message = completion['choices'][0]['message']['content']
    return message

def message_langchain(message):
    custom_message = f'Trả lời bằng tiếng việt: {message}'
    data = {"question": custom_message}
    completion = requests.post('http://localhost:3010/api/zalo/chat', json=data)
    if completion.status_code == 200:
        print('Response ok')
        return completion.json()
    else:
        completion = 'Error'
        return completion
def handle_messages(message):
    if message == 'Đưa cho tôi một câu nói truyền cảm hứng cho hôm nay':
        result = message_gpt(message)
        return result
    else:
        completion = message_langchain(message)
        print('langchain handling...')
        if completion == 'Error':
            return 'Server hiện đang quá tải. Vui lòng thử lại sau 10 giây! Thành thật xin lỗi đến bạn.'
        else:
            result = completion['text']
            print(completion)
            except_word = ['sorry', 'không được đề cập tên trong đoạn văn', 'được cung cấp trong đoạn văn trên',
                           'không biết', 'không rõ', "i don't know.", 'tôi không biết',
                           'không thể trả lời được câu hỏi này với thông tin cung cấp', 'i am an ai',
                           'không liên quan đến ngữ cảnh được cung cấp',
                           'xin lỗi, tôi không thể trả lời câu hỏi này',
                           'thông tin được cung cấp',
                           'nội dung đã cung cấp', 'xin lỗi', 'ngữ cảnh']
            form = ['https://forms.gle/6JL1c6UoCHm2WNZi7']
            if any(keyword in result.lower() for keyword in form):
                return result
            elif any(keyword in result.lower() for keyword in except_word):
                message = "Bạn hãy đóng vai đại diện cho trường cao đẳng viễn đông và trả lời bằng tiếng việt, ngắn gọn, không vượt quá 1000 ký tự, tranh lặp từ: " + message
                result = message_gpt(message)
            return result

def send_messages(access_token, message, message_data, thread, change_action):
    sender_id = message_data['sender']['id']
    data = {
      "recipient": {
        "user_id": sender_id
      },
      "message": {
        "text": message
      }
    }
    headers = {'access_token': access_token}

    response = requests.post('https://openapi.zalo.me/v2.0/oa/message', headers=headers, json=data)

    if response.ok:
        if change_action:
            add_action(sender_id, thread, 'None')
        check_entry_message(message_data)
    else:
        print('Lỗi khi gửi tin nhắn: ', response.content)

    return response
def send_message_with_buttons(access_token, message, message_data, thread, change_action):
    print('Message before check status gpt: ', message)
    if message_data['event_name'] == 'user_click_chatnow':
        sender_id = message_data['user_id']
    else:
        sender_id = message_data['sender']['id']
    opt = 1
    use_gpt = True

    thread_actions = {'Contact': {'opt': 2, 'use_gpt': False},
                      'Infor Collage': {'opt': 0, 'use_gpt': False},
                      'Open gpt': {'opt': 3, 'use_gpt': True},
                      'Student chat': {'opt': 0, 'use_gpt': True},
                      'Parents chat': {'opt': 0, 'use_gpt': True},
                      'Close gpt': {'opt': 0, 'use_gpt': False},
                      'ChatNow': {'opt': 1, 'use_gpt': False}}

    if thread is None:
        add_action(sender_id, thread, 'None')
    else:
        thread_action = thread['actions']
        if thread_action in thread_actions.keys():
            opt = thread_actions[thread_action]['opt']
            use_gpt = thread_actions[thread_action]['use_gpt']
            if thread_action == 'Infor Collage' and message != 'Bạn muốn biết thêm gì về trường?':
                message = handle_messages(message)
        elif thread_action == 'Open gpt':
            opt = 3
        elif thread_action in ['Student chat', 'Parents chat', 'Close gpt']:
            opt = 0
            if thread_action == 'Close gpt':
                use_gpt = False

    block_word = ['Bạn cần thêm gì không?', 'Contact', 'Bạn là ai?', 'Bạn muốn biết thêm gì về trường?', 'Hãy cho tôi biết bạn muốn chat với ai?']
    if any(keyword in message for keyword in block_word):
        use_gpt = False
    else:
        basic_message = message_data['message']['text']
        send_messages(access_token, f'Đang trả lời: {basic_message}...', message_data, thread, False)

    if message == 'New user':
        message = 'Xin chào! Tôi là Chatbot của trường Cao đẳng Viễn Đông. Rất vui được gặp bạn! Để giúp bạn có được hỗ trợ chính xác nhất, hãy lựa chọn các nút bên dưới.' \
                  '\nNếu bạn đang sử dụng Zalo trên máy tính hoặc website, hãy thực hiện các bước tương ứng với nhu cầu của bạn:' \
                  '\n1.Rút gọn đoạn văn: Chat "Rút gọn đoạn văn" và gửi đoạn văn của bạn để tôi có thể giúp bạn rút gọn nó.' \
                  '\n2.Lời động viên: Chat "Motivation quotes" để nhận được một câu truyền động lực của ngày hôm nay.' \
                  '\n3.Tư vấn và trò chuyện: Chat "Tư vấn và trò chuyện" để bắt đầu cuộc trao đổi với tôi. Tại đây, bạn có thể lựa chọn:' \
                  '\n    -Chat với GPT: Nếu bạn muốn trò chuyện với Chat GPT mà không cần tạo tài khoản, hãy chat "Chat với GPT". Hệ thống sẽ hỏi bạn là "phụ huynh" hay "học sinh/sinh viên", bạn chỉ cần trả lời một trong hai là được.' \
                  '\n    -Chat với tư vấn viên: Nếu bạn muốn tư vấn với tư vấn viên, hãy chat "Chat với tư vấn viên".' \
                  '\n    -Hỏi về thông tin trường: Nếu bạn có bất kỳ thắc mắc nào về thông tin trường, hãy chat "Hỏi về thông tin trường".' \
                  '\n4.Kết thúc: Chat "Kết thúc" để trở về cuộc hội thoại đầu tiên.' \
                  '\nVui lòng chỉ hỏi trong 1 lần nhắn cho một lần hỏi.' \
                  '\nChúc bạn có một cuộc trò chuyện vui vẻ và tôi hy vọng tôi có thể giúp đỡ bạn. Xin cảm ơn đã ghé thăm!'
        use_gpt = False
    if use_gpt:
        try:
            if thread['actions'] == 'Student chat':
                message = message_gpt(message)
            else:
                message = handle_messages(message)
        except Exception as e:
            message = 'Server hiện đang quá tải. Vui lòng thử lại sau 10 giây! Thành thật xin lỗi đến bạn.'
            print('Error from gpt: ', e)

    button_payload = options_button(opt)

    payload = {
        "recipient": {
            "user_id": sender_id
        },
        "message": {
            "text": message,
            "attachment": {
                "type": "template",
                "payload": button_payload
            }
        }
    }

    headers = {
        'access_token': access_token
    }

    response = requests.post('https://openapi.zalo.me/v2.0/oa/message', headers=headers, json=payload)

    if response.ok:
        if change_action and thread is not None:
            add_action(sender_id, thread, 'None')
        check_entry_message(message_data)
    else:
        print('Lỗi khi gửi tin nhắn: ', response.content)
    return response
def push_notification():
    pass
@app.route("/", methods=['POST'])
def zalowebhook():
    data = request.get_json()
    print(data)
    access_token = get_zalo_access_token()
    opt_action = ['None', 'Short poem', 'Contact', 'Open gpt', 'Close gpt', 'Student chat', 'Parents chat', 'Infor Collage']
    admin_ids = [
        '6506618071425485644',  # Phung
        '4356460878800442485',  # Tien
        '7271633110143013866',  # Tan
        '3476303423703683902',  # Huy Pham
        '2113705009586525525',  # thay Quang
        '788668026204874481',  # Tra
        '4274857781779133779',  # An
        '7503028259859617056',
        # '4340870641274723389', Hoa
        # '4608521476843394804',Kato
        # '734625170260567601',Nam
        '973327464555352449',  # thay Cuong
        '3183865047226326575',
        '1363997715039937261',
        '1727941565938495738',
        '2791901097215985086',
        '4827922608283475456',  # hao
        # PDT
        '8233721260538997572',
        '3012567826792217294',
        '2679719179042883632',
        '9204948562308717758',
        '7659531353712180044',
        '6027697670083405990'#Duong
    ]

    if data['event_name'] == 'user_click_chatnow':
        message = 'New user'
        user_id = data['user_id']
        now = datetime.now()
        thread = {'sender_id': user_id, 'created_at': now, 'actions': 'None'}
        thread_collection.insert_one(thread)

        send_message_with_buttons(access_token, message, data, thread, False)
        add_action(user_id, thread, 'None')
        return '200 OK HTTPS.', 200
    message_local = check_entry_message(data)
    duplicated = "duplicated" if message_local is not None else "new"
    print(duplicated)
    if duplicated == "duplicated":
        return '200 OK HTTPS.', 200

    try:
        if message_local is None:
            sender_id = data['sender']['id']
            message = data['message']['text']
            thread = get_recent_thread(sender_id)

            if sender_id not in admin_ids:
                print(sender_id)
                return '200 OK HTTPS.', 200

            if thread['actions'] == opt_action[1]:
                message_question = 'Hãy rút gọn đoạn văn sau bằng tiếng việt, giữ lại nhưng ý chính: \n' + message
                send_message_with_buttons(access_token, message_question, data, thread, True)
            elif thread['actions'] == opt_action[2]:
                if message.lower() == 'chat với gpt':
                    add_action(sender_id, thread, opt_action[3])
                    send_message_with_buttons(access_token, 'Bạn là ai?', data, thread, False)
                elif message.lower() == 'chat với tư vấn viên':
                    add_action(sender_id, thread, opt_action[4])
                    send_message_with_buttons(access_token, 'Vui lòng đợi tư vấn viên phản hồi!', data, thread, False)
                elif message.lower() == 'hỏi về thông tin trường':
                    add_action(sender_id, thread, opt_action[7])
                    send_message_with_buttons(access_token, 'Bạn muốn biết thêm gì về trường?', data, thread, False)
                else:
                    send_message_with_buttons(access_token, 'Vui lòng chỉ chọn lựa chọn trên!', data, thread, False)
            elif thread['actions'] == opt_action[3] or thread['actions'] == opt_action[5] or thread['actions'] ==  opt_action[6]:
                if message.lower() == 'phụ huynh':
                    message_question = 'Hãy chào vị phụ huynh bằng bằng tiếng việt lịch sự'
                    add_action(sender_id, thread, opt_action[6])
                    send_message_with_buttons(access_token, message_question, data, thread, False)
                elif message.lower() in ['học sinh/sinh viên', 'học sinh', 'sinh viên']:
                    add_action(sender_id, thread, opt_action[5])
                    send_message_with_buttons(access_token, 'Bạn muốn biết thêm gì về trường?', data, thread, False)
                elif message.lower() == 'kết thúc':
                    add_action(sender_id, thread, 'None')
                    send_message_with_buttons(access_token, 'Bạn cần thêm gì không?', data, thread, False)
                else:
                    message_question = message
                    send_message_with_buttons(access_token, message_question, data, thread, False)
            elif thread['actions'] == opt_action[4]:
                add_action(sender_id, thread, opt_action[4])
                if message.lower() == 'kết thúc':
                    add_action(sender_id, thread, 'None')
                    send_message_with_buttons(access_token, 'Bạn cần thêm gì không?', data, thread, True)
            elif thread['actions'] == opt_action[7]:
                add_action(sender_id, thread, opt_action[7])
                if message.lower() == 'kết thúc':
                    add_action(sender_id, thread, 'None')
                    send_message_with_buttons(access_token, 'Bạn cần thêm gì không?', data, thread, True)
                else:
                    send_message_with_buttons(access_token, message, data, thread, False)
            elif thread['actions'] == 'None':
                if message.lower() in ['rút ngắn đoạn văn', 'rút gọn đoạn văn']:
                    add_action(sender_id, thread, 'Short poem')
                    send_messages(access_token, 'Vui lòng nhập đoạn văn cần rút gọn', data, thread, False)
                elif message.lower() == "motivation quotes":
                    message_question = "Đưa cho tôi một câu nói truyền cảm hứng cho hôm nay"
                    send_message_with_buttons(access_token, message_question, data, thread, False)
                elif message.lower() == 'tư vấn và trò chuyện':
                    add_action(sender_id, thread, 'Contact')
                    send_message_with_buttons(access_token, 'Hãy cho tôi biết bạn muốn chat với ai?', data, thread, False)
                else:
                    message_question = message
                    send_message_with_buttons(access_token, message_question, data, thread, True)
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Error', 500
    return '200 OK HTTPS.', 200

if __name__ == '__main__':
    app.run(port=5001)