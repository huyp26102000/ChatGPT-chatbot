import threading
import pika
from flask import Flask, request
import threading
import time
import json
import requests

# PORT IN OUT ZALO
PORT_INPUT = 5000
URL_OUTPUT_MESS = 'http://localhost:5002/'
URL_OUTPUT_ZALO = 'http://localhost:5001/'

# QUEUE 
QUEUE_ZALO = 'zalo_queue_server'
QUEUE_MESS = 'messenger_queue_server'
time_sleep = 6
#Điều kiện xử lí
CONDITION = 'entry'

# Hàm lắng nghe tin nhắn từ hàng đợi
def consume_messages_zalo():
    connection_zalo = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel_zalo = connection_zalo.channel()
    channel_zalo.queue_declare(queue=QUEUE_ZALO, exclusive=True )
    def callback(ch, method, properties, body):
        json_data = json.loads(body)
        response = requests.post(URL_OUTPUT_ZALO, json=json_data)
        if response.status_code == 200:
            print("Result")
        else:
            print('Request failed with status code:', response.status_code)
        time.sleep(time_sleep)

    channel_zalo.basic_qos(prefetch_count=1)
    channel_zalo.basic_consume(queue=QUEUE_ZALO, on_message_callback=callback, auto_ack=True)
    channel_zalo.start_consuming()
    

def consume_messages_mess():
    connection_mess = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel_mess = connection_mess.channel()
    channel_mess.queue_declare(queue=QUEUE_MESS, exclusive=True )
    # queue_name_mess = result_mess.method.queue
    def process_message_mess(ch, method, properties, body):
        json_data = json.loads(body)
        response = requests.post(URL_OUTPUT_MESS, json=json_data)
        if response.status_code == 200:
            print("Result")
        else:
            print('Request failed with status code:', response.status_code)
        time.sleep(time_sleep)
    channel_mess.basic_qos(prefetch_count=1)
    channel_mess.basic_consume(queue=QUEUE_MESS, on_message_callback=process_message_mess, auto_ack=True)
    channel_mess.start_consuming()



def FlaskZaloAndMessWeb() :
    
    app_zalo = Flask(__name__)
    @app_zalo.route('/', methods=['POST'])
    def send_message_zalo():
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        data = request.get_json()
        json_data = json.dumps(data)
        # Kết nối với RabbitMQ
        data = request.get_json()
        if data.get('entry'):
            try:
                channel.basic_publish(exchange='', routing_key=QUEUE_MESS, body=json_data)
            except pika.exceptions.StreamLostError:
                connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
                channel = connection.channel()
                channel.basic_publish(exchange='', routing_key=QUEUE_MESS, body=json_data)
            
        else:
            try:
                channel.basic_publish(exchange='', routing_key=QUEUE_ZALO, body=json_data)
            except pika.exceptions.StreamLostError:
                connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
                channel = connection.channel()
                channel.basic_publish(exchange='', routing_key=QUEUE_ZALO, body=json_data)
            
        return "Message sent to RabbitMQ", 200
    app_zalo.run(port=PORT_INPUT)

thread_zalo = threading.Thread(target=consume_messages_zalo)
thread_zalo.start()

thread_mess = threading.Thread(target=consume_messages_mess)
thread_mess.start()

if __name__ == '__main__':

    flask_thread_zalo = threading.Thread(target=FlaskZaloAndMessWeb)
    flask_thread_zalo.start()

