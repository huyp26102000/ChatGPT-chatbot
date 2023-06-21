# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import openai
import requests
from flask import Flask, request
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['Messenger-chatbot']
thread_collection = db['thread']
message_collection = db['message']

PAGE_ACCESS_TOKEN = open(".messenger_token", "r").read()
openai.api_key = open(".gpt_api_key", "r").read()
privacyPolicyRender = open("privacy-policy.html", "r").read()
termConditionRender = open("term-of-condition.html", "r", encoding="utf8").read()

app = Flask(__name__)
API = "https://graph.facebook.com/v16.0/me/messages?access_token=" + PAGE_ACCESS_TOKEN
PORT = 5002

@app.route("/", methods=['GET'])
def fbverify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == "anystring-verify":
            return "Verification token missmatch", 403
        print(request.args['hub.challenge'], 200)
        return request.args['hub.challenge'], 200
    return "OK", 200


def get_recent_thread(sender_id):
    five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
    thread = thread_collection.find_one({'sender_id': sender_id, 'created_at': {'$gt': five_minutes_ago}})
    if thread is None:
        # Create a new document if not found
        thread = {'sender_id': sender_id, 'created_at': datetime.utcnow(), 'actions': []}
        thread_collection.insert_one(thread)
        return None
    else:
        return thread


def add_action(thread, action_code):
    now = datetime.utcnow()
    thread['actions'].append({'code': action_code, 'created_at': now})
    thread['created_at'] = now
    thread_collection.replace_one({'_id': thread['_id']}, thread, upsert=True)


def message(sender_id, message):
    request_body = {
        "recipient": {
            "id": sender_id
        },
        "message": {
            "text": message
        }
    }
    response = requests.post(API, json=request_body).json()
    print(response)
    return response


def message_gpt(chatgpt_message):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": chatgpt_message},
        ]
    )
    # request_body = {
    #     "recipient": {
    #         "id": sender_id
    #     },
    #     "message": {
    #         "text": completion['choices'][0]['message']['content']
    #     }
    # }
    # response = requests.post(API, json=request_body).json()
    # print(response)
    return completion['choices'][0]['message']['content']

def education_option(sender_id, thread, data):
    request_body = {
        "recipient": {
            "id": sender_id
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": "Tư vấn và trò chuyện",
                    "buttons": [
                        {
                            "type": "postback",
                            "title": "Tiến độ ra trường",
                            "payload": "payload_4#0",
                        },
                        {
                            "type": "postback",
                            "title": "Cập nhật điểm số",
                            "payload": "payload_4#1",
                        },
                        {
                            "type": "postback",
                            "title": "Cập nhật học phí",
                            "payload": "payload_4#2",
                        },
                    ]
                }
            }
        }
    }

    response = requests.post(API, json=request_body).json()
    print(response)
    return response

def conversation_option(sender_id, thread, data):
    request_body = {
        "recipient": {
            "id": sender_id
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": "Tư vấn và trò chuyện",
                    "buttons": [
                        {
                            "type": "postback",
                            "title": "Tư vấn tuyển sinh",
                            "payload": "payload_4",
                        },
                        {
                            "type": "postback",
                            "title": "Chat với GPT",
                            "payload": "payload_5",
                        },
                        {
                            "type": "postback",
                            "title": "Hỏi đáp",
                            "payload": "payload_6",
                        },
                    ]
                }
            }
        }
    }

    response = requests.post(API, json=request_body).json()
    print(response)
    return response

def message_option_gpt(sender_id, thread, data):
    request_body = {
        "recipient": {
            "id": sender_id
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": "What do you want to do next?",
                    "buttons": [
                        {
                            "type": "postback",
                            "title": "Kết thúc trò chuyện",
                            "payload": "payload_3",
                        },
                    ]
                }
            }
        }
    }

    response = requests.post(API, json=request_body).json()
    print(response)
    return response

def message_option(sender_id, thread, data):
    request_body = {
        "recipient": {
            "id": sender_id
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": "What do you want to do next?",
                    "buttons": [
                        {
                            "type": "postback",
                            "title": "Rút ngắn đoạn văn",
                            "payload": "payload_1",
                        },
                        {
                            "type": "postback",
                            "title": "Motivation quote",
                            "payload": "payload_2",
                        },
                        {
                            "type": "postback",
                            "title": "Tư vấn và trò chuyện",
                            "payload": "payload_3",
                        },
                    ]
                }
            }
        }
    }

    response = requests.post(API, json=request_body).json()
    print(response)
    return response


def postback(thread, data):
    pass


def check_entry_message(message_data):
    messaging = message_data['entry'][0]['messaging'][0]
    message_id = None
    if "postback" in messaging:
        message_id = messaging['postback']['mid']
    if "message" in messaging:
        message_id = messaging['message']['mid']

    message = message_collection.find_one({'message_id': message_id})
    if message is None:
        # Create a new document if not found
        new_message = {'message_id': message_id, 'data': message_data}
        message_collection.insert_one(new_message)
        return None
    return message

def message_langchain(question):
    custom_message = 'Trả lời bằng tiếng việt: ' + question
    data = {"question": custom_message}
    completion = requests.post('http://localhost:3010/api/messenger/chat', json=data)
    if completion.status_code == 200:
        print('Response ok')
        return completion.json()
    else:
        completion = 'Error'
        return completion

def handle_message(message):
    custom_message = f'hãy trả lời câu hỏi bằng tiếng việt ngắn gọn: {message}'
    completion = message_langchain(custom_message)
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
        if any(keyword in result.lower() for keyword in except_word):
            print('Except word')
            custom_message = f"Bạn hãy đóng vai đại diện cho trường cao đẳng viễn đông và trả lời bằng tiếng việt, ngắn gọn, không vượt quá 1000 ký tự, tranh lặp từ: {message}"
            result = message_gpt(custom_message)
            print(result)
        return result

def generate_question(question):
    # custom_message = 'Trả lời bằng tiếng việt: ' + question
    # data = {"question": custom_message}
    # completion = requests.post('http://localhost:3010/api/chat', json=data)
    # if completion.status_code == 200:
    #     print('Response ok')
    #     return completion.json()
    # else:
    #     completion = 'Error'
    #     return completion
    return f"""đoạn văn sau đây và vào vai là trường cao đẳng viễn đông, trả lời những câu hỏi như bình thường, nếu câu hỏi có liên quan đến trường cao đẳng viễn đông thì lấy dữ liệu từ đoạn văn sau. nếu câu hỏi không liên quan thì cứ trả lời bình thường không cần tìm dữ liệu trong đoạn bên dưới và đừng nói có liên quan đến cao đẳng viễn đông hay không
 "Cao Đẳng Viễn Đông:
Thông tin: address: Lô 2,Công viên phần mềm Quang Trung,P.Tân Chánh Hiệp,Quận 12,thành phố HCM.Official web: www.viendong.edu.vn.admission page www.tuyensinh.viendong.edu.vn.Hotline: 02838911111/0933734474/0933634400/0977334400.Support Zalo,Facebook,Viber,Youtube với tên Cao đẳng Viễn Đông.Email contact@viendong.edu.vn.
trường có 12 tầng lầu và sau đây là vị trí các ngành được dạy: “Ô tô.Cơ khí.Xây dựng: xưởng thực hành tầng hầm.xưởng cạnh cateen.Điện – Điện tử: tầng 8.nhà điện năng lượng mặt trời (sân trước).Du lịch.Nhà hàng – khách sạn: lầu 1,2 căn teen (nghiệp vụ bàn,bar,bếp),lầu 8 (nghiệp vụ buồng),phòng thực hàng 5 sao lần 10 (nghiệp vụ buồng,phòng),phòng H3 lầu 8 (nghiệp vụ lễ tân).Lập trình: phòng máy C1,C5,C6 (lầu 3) và H1 (lầu 8),phòng lab lầu 2.Thiết kế đồ họa: phòng thực hành D9,D11.Truyền thông & Mạng máy tính: Phòng server lầu 7.Khối ngành Kinh tế: phòng mô phỏng thực hành và khởi nghiệp: lầu 7 và H3 lầu 8.Khối ngành Chăm sóc sắc đẹp: Lầu 6 (Spa Massage),7 (phun xăm thêu trên da),8 (tóc,móng,trang điểm).Khối ngành Ngoại ngữ: CLB Ngoại ngữ và phòng Lap lầu 2.Khối ngành Chăm sóc sức khỏe: Lầu 6 (Điều dưỡng),Lầu 7,8 (Xét nghiệm y học).Thư viện lầu 6.Có sân bóng đá,bóng bàn.bóng rổ.bóng chuyển.bóng bàn.sân sinh hoạt tập thể.Có phòng tự học”
Thông tin ngành nghề đào tạo:
Hệ Cao đẳng:6 khối ngành gồm20 ngành:(Khối Công nghệ:5 ngành(Lập trình ứng dụng;Truyền thông và Mạng máy tính;Thiết kế đồ họa(bao gồm cả Truyền thông đa phương tiện)), Khối Dịch vụ:2 ngành(QT Nhà hàng và Khách sạn/QT Dịch vụ Du lịch & Lữ hành).Khối Chăm sóc sức khỏe:4 ngành(Điều dưỡng/Hộ sinh/Xét nghiệm y học/Chăm sóc sắc đẹp).Khối Kinh tế:6 ngành(QTKD;QT Marketing(bao gồm Quan hệ công chúng);Kế toán;Tài chính–Ngân hàng;QT Văn phòng;Logistics))
Hệ Trung cấp gồm 6 ngành: Tin học ứng dụng; Quản lý doanh nghiệp; Kế toán doanh nghiệp; Khai thác và Sửa chữa Thiết bị Cơ khí; Điện công nghiệp và Dân dụng; Tài chính – Ngân hàng; Tạo mẫu & Chăm sóc sắc đẹp; Nghiệp vụ Nhà hàng – Khách sạn; Kỹ thuật chế biến món ăn
Hệ Đại học từ xa; Vừa học-Vừa làm; Liên thông; Văn bằng 2 của ĐH Kinh tế TP. HCM; ĐH Mở và ĐH Cần Thơ: bằng cấp tương đương chính quy (tháng 01/03/2020 tất cả văn bằng đại học đều không ghi hình thức đào tạo theo thông tư 27/2019/TT-BGD&ĐT), các trường hỗ trọ là: Đại học Kinh tế TP. HCM: QTKD; Kế toán; Tài chính – Ngân hàng; QT Văn phòng; QT Nhà hàng – Khách sạn; QT DV Du lịch & Lữ hành; Công nghệ thông tin; Tin học quản lý; Tiếng Anh; Luật; Quản lý công. Đại học Sư phạm Kỹ thuật TPHCM: Ô tô, Cơ khí, Chế tạo máy, Điện – Điện tử, CNTT, Đồ họa, Tiếng Anh. Đại học Mở: QTKD; Kế toán; Ngôn ngữ Anh; Luật kinh tế; Luật; CNKT Xây dựng Đại học Giao thông vận tải TPHCM: Ô tô, Cơ khí, Điện điện tử, Xây dựng, Khoa học máy tính, Logistics. Đại học Cần Thơ: Cơ khí; Điện – Điện tử; Xây dựng; Việt Nam học; Hướng dẫn viên du lịch; Nhà hàng – Khách sạn; Luật; QTKD; Marketing; Kế toán; Tài chính – Ngân hàng; Công nghệ thông tin; Ngôn ngữ Anh”
Có cơ hội du học tại các trường sau đây: Đại học Valdosta-Mỹ(các ngành Công nghệ thông tin; Kế toán; Tài chính – Ngân hàng; QTKD), Du học và làm việc CHLB Đức(các ngành Điều dưỡng; Nhà hàng – Khách sạn; Chăm sóc sắc đẹp; Cơ khí; Ô tô; Xây dựng; Bếp), Du học Úc (Trường Dự bị Đại học UPC; trường Đại học KOI)(các ngành Quản trị và Kinh doanh; Tiếp thị và Truyền thông; Anh văn Sư phạm; Giáo dục Mầm non), Cao đẳng Daelim, Hàn Quốc: (các ngành Nhà hàng – Khách sạn; Du lịch; Ô tô; Quản trị kinh doanh; Thiết kế đồ họa), Đại học Đông Chu; Hiệp hội Chăm sóc sắc đẹp IBES, Hàn Quốc ngành Chăm sóc sắc đẹp, Cao đẳng Nakanihon(ngành CNKT Ô tô)
Các chương trình liên thông:
Từ Trung cấp lên Cao đẳng: 8 tháng đến 1 năm
Từ Sơ cấp lên Trung cấp: 8 tháng đến 1 năm
Từ Sơ cấp lên Cao đẳng: 2 năm
Tư Cao đẳng lên Đại học: 1 đến 1.5 năm
Từ Trung cấp lên Đại học: từ 2 đến 2.5 năm
Đầu vào CĐ Viễn Đông; đầu ra Đại học: ĐH Kinh tế TP. HCM; ĐH Sư phạm Kỹ thuật TPHCM, ĐH GTVT TPHCM; ĐH Mở TP. HCM; ĐH Cần Thơ (Từ ngày 01/07/2019: bằng Đại học từ xa; văn bằng 2; vừa học vừa làm có giá trị như bằng chính quy, trên bằng không còn ghi hình thức đào tạo nữ; được thi công chức vào nhà nước và được học tiếp lên thạc sĩ, mọi chế độ về ngạch bậc lương tương đương với trình độ): đến 1.5 năm (tốt nghiệp CĐ đúng chuyên ngành)
2 đến 2.5 năm (tốt nghiệp Trung cấp đúng chuyên ngành)
3.5 đến 4 năm (tốt nghiệp THPT: 2 bằng CĐ Viễn Đông và 1 trong 5 bằng ĐH của các trường nêu trên, đăng ký học 2 chuyên ngành cùng lúc)
Điều kiện Nếu muốn Du học Mỹ: liên kế ĐH Valdosta: 2+2 hoặc 1+3; Điều kiện: Ielts 6.0 (có lớp dự bị nếu không đạt chuẩn Tiếng Anh, hỗ trợ làm thêm)

Các điểm khác biệt tại CĐ Viễn Đông:
Về cơ hội việc làm: Có việc làm đúng ngành
Được trường ký cam kết đảm bảo việc làm cho SV sau khi tốt nghiệp.
Được thực tập và làm việc tại các DN, BV lớn(thực tập cuối khóa thường có lương): được thực tập ngay từ HK2 của năm 1 tại bệnh viên Chợ Rẫy; Nhi đồng; BV Bệnh nhiệt đới; Hùng Vương;… Khách sạn Rex; Lyberty; Đông Phương Group; PQC (White palace; Gem Center; The Log) Vinpearl (VinGroup); SunGroup; Toyota; SG Ford; Samco; Misa; TMA; Global Cybefsoft; Digitex; SPS; ANC Logistics; Nguyễn Ngọc Logistcis …
Được giới thiệu việc làm bán thời gian ngay khi vừa hoàn tất thủ tục nhập học với mức lương dao động từ 3 đến 6.5 triệu/tháng tại các doanh nghiệp cạnh trường Cao đẳng Viễn Đông (ngay trong khu QTSC): xử lý dữ liệu; telesales; nhà hàng, khách sạn, siêu thị, metrol; rạp chiếu phim; shop quần áo; café văn phòng;…
Được học, làm việc và định cư tại nước ngoài cao: Đức, Úc, Nhật, Mỹ

Về cơ hội: Có bằng đại học tốp trên
Được cấp 2 bằng Đại học và Cao đẳng trong thời gian 3.5 năm (Đầu vào Cao đẳng Viễn Đông; đầu ra Đại học tốp trên: Đại học Kinh tế TP. HCM; ĐH Sư phạm Kỹ thuật TPHCM; ĐH GTVT TPHCM; ĐH Mở; ĐH Cần Thơ)
Về chất lượng đào tạo được công nhận cả trong và ngoài nước:Là trường tư thục duy nhất có sinh viên được trao tặng bằng khen HSSV giỏi, tiêu biểu toàn quốc: 07 sinh viên (2021); 03 sinh viên (2022). Là trường 04 năm liền được UBND TPHCM trao cờ thi đua và bằng khen hoàn thành xuất sắc nhiệm vụ năm học. Là trường tư thục duy nhất có SV đoạt giải nhì hội thi khởi nghiệp Startup Kite 2022 toàn quốc: đã và đang được doanh nghiệp tài trợ 2 tỷ đồng để phát triển dự án Apps DefiMap để đưa vào sử dụng thực tế tại các bệnh viện trong thời gian tới. Là trường được các nước trên thế giới công nhận: Mỹ (chương trình liên thông 2+2 với ĐH Valdosta, Mỹ); Đức (chương trình 2+2 học nghề miễn phí tại CHLB Đức); Úc (Chương trình liên kết với Cao đẳng dự bị Đại học UPC). Là trường có tỷ lệ học sinh chương trình 9+ tham dự kỳ thi tốt nghiệp THPT 2022 đạt kết quả cao nhất quận: 99,44%.Là trường tư thục duy nhất đã áp dụng Apps viendong edu để SV và GV tra cứu các vấn đề về học tập và giảng dạy."
Câu hỏi của tôi là: "{question}"""

@app.route("/", methods=['POST'])
def fbwebhook():
    data = request.get_json()
    print("facebook: ", data)
    message_local = check_entry_message(data)
    if message_local is not None:
        print("duplicate")
        return '200 OK HTTPS.'
    else: print("new")
    try:
        if message_local is None:
            # Read messages from facebook messanger.
            sender_id = data['entry'][0]['messaging'][0]['sender']['id']
            print(sender_id)
            thread = get_recent_thread(sender_id)
            if thread is None:
                message_option(sender_id, thread, data)
            else:
                message_data = data["entry"][0]["messaging"][0]
                if "postback" in message_data:
                    user_message = data['entry'][0]['messaging'][0]['postback']
                    print(user_message)
                    payload = message_data['postback']['payload']
                    print(payload)
                    add_action(thread, payload)
                    if payload == "payload_1":
                        message(sender_id, "Vui lòng nhập đoạn văn cần rút gọn")
                    if payload == "payload_2":
                        message_handle = handle_message("Đưa cho tôi một câu nói truyền cảm hứng cho hôm nay")
                        message(sender_id, message_handle)
                        message_option(sender_id, thread, data)
                    if payload == "payload_3":
                        conversation_option(sender_id, thread, data)
                    if payload == "payload_4":
                        education_option(sender_id, thread, data)
                    if payload == "payload_5":
                        # education_option(sender_id, thread, data)
                        message(sender_id, "Bây giờ bạn sẽ trò chuyện với GPT")
                    if payload == "payload_6":
                        handle_message(user_message)
                        message_option_gpt(sender_id, thread, data)
                    if "#" in payload:
                        option = payload.split('#')[1]
                        if int(option) < 3:
                            message(sender_id, "Hãy điền vào form để được hỗ trợ: https://forms.gle/6JL1c6UoCHm2WNZi7")
                            education_option(sender_id, thread, data)
                else:
                    direct_message = message_data['message']['text']
                    print(f'message {direct_message}')
                    actions = thread['actions']
                    print(len(actions))
                    if len(actions) == 0:
                        current_action = None
                        message_from_gpt = handle_message(direct_message)
                        message(sender_id, message_from_gpt)
                    else:
                        current_action = actions[len(actions) - 1]
                    if current_action is not None:
                        if current_action['code'] == 'payload_1':
                            message_from_gpt = message_gpt(f'rút gọn đoạn văn sau đây, giữ lại những ý chính: "{direct_message}"')
                            message(sender_id, message_from_gpt)
                            message_option(sender_id, thread, data)
                            print('we here')
                        elif current_action['code'] == 'payload_5':
                            message_from_gpt = handle_message(direct_message)
                            message(sender_id, message_from_gpt)
                            message_option_gpt(sender_id, thread, data)
                            print('no, we here')
                        else:
                            message_from_gpt = handle_message(direct_message)
                            message(sender_id, message_from_gpt)
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
    app.run(port=PORT)
