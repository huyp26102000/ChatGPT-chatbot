import pika
from flask import Flask, request
import threading
import time
import json
import requests

# connect to RabbitMQ server
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
port = 5000
url_zalo = 'http://localhost:5001/'
url_messenger = 'http://localhost:5002/'
time_request = 3

# # get authentication from ZaloWebhook
requests.get(url_zalo)
#
# # get authentication from MessengerWebhook
requests.get(url_messenger)

# exchange variable declaration
channel.exchange_declare(exchange='zalo_exchange_server', exchange_type='fanout')

# queue variable declaration
queue_name = ''
result = channel.queue_declare(queue=queue_name, exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange='zalo_exchange_server', queue=queue_name) 
queue_name1 = result.method.queue

def process_message(ch, method, properties, body):
    json_data = json.loads(body)
    print(json_data)
    try:
        if json_data.get('entry'):
            response = requests.post(url_messenger, json=json_data)
        else:
            response = requests.post(url_zalo, json=json_data)
        if response.ok:
            print('result')
        else:
            print('Request failed with status code:', response.status_code)
        time.sleep(time_request)
    except Exception as e:
        print(e)

# thread message from rabbit
def consume_messages():
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=process_message, auto_ack=True)
    channel.start_consuming()

thread = threading.Thread(target=consume_messages)
thread.start()

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verifier():
    return 'HTTPS OK, 200', 200

@app.route('/', methods=['POST'])
def send_message():
    data = request.get_json()
    # convert requests to JSON
    json_data = json.dumps(data)
    channel.basic_publish(exchange='zalo_exchange_server', routing_key='', body=json_data)
    return 'Message sent to RabbitMQ'

if __name__ == '__main__':
    app.run(port=port)