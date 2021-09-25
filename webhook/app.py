from json import dumps
from flask import Flask, request, jsonify
import pika

app = Flask(__name__)


@app.route('/')
def index():
    return 'OK'


@app.route('/alert', methods=['POST'])
def alert():
    """Create an alert"""
    message = request.get_json()
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='monapp_alerts', durable=True)
    channel.basic_publish(
        exchange='',
        routing_key='monapp_alerts',
        body=dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ))
    connection.close()
    return dumps({'success': True}), 200, {'ContentType': 'application/json'}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
    