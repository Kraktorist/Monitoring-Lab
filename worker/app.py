import json
import time
import pika
import requests

SLEEPTIME = 10
print(' [*] Sleeping for ', SLEEPTIME, ' seconds.')
time.sleep(30)

print(' [*] Connecting to server ...')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='task_queue', durable=True)

print(' [*] Waiting for messages.')

def callback(ch, method, properties, body):
    print(" [x] Received a message")
    body = json.loads(body.decode())
    print(body['alerts'][0]['annotations']['description'])
    if body['alerts'][0]['labels']['alertname'] == 'LowWarehouseVolume':
        command = 'start'
    if body['alerts'][0]['labels']['alertname'] == 'HighWarehouseVolume':
        command = 'stop'
    if command:
        uri = f"http://monapp:5000/switch/{ body['alerts'][0]['labels']['position'] }/{ command }"
        r = requests.get(url=uri)
        print(f' [*] Response {r.text}')
        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        print('Unknown command')


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_queue', on_message_callback=callback)
channel.start_consuming()
