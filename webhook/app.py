import logging
import sys


from json import dumps
from flask import Flask, request


log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

logger = logging.getLogger('webhook')
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',  datefmt='%a, %d %b %Y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)

app = Flask(__name__)



@app.route('/')
def main():
    """Main page"""


@app.route("/alert", methods=['POST'])
def alert():
    """Creates an alert"""
    message = request.get_json()
    print(message)
    logger.fatal("%s. Alert has been created", {message['commonAnnotations']['summary']})
    return dumps({'success': True}), 200, {'ContentType': 'application/json'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5001', debug=False)
