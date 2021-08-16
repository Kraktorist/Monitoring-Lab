from flask import Flask, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Gauge
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from gibberish import Gibberish
from json import dumps, loads
from datetime import datetime
from time import time
from math import sin, pi, cos
from random import randint, random

import logging
import sys
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

logger = logging.getLogger('monapp')
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',  datefmt='%a, %d %b %Y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_data2():
  return round(10+10*random()+cos(2*pi*datetime.now().second/60), 4)


def get_data():
  x = datetime.now().second
  if datetime.now().minute % randint(2,7) == 0 & x in range(1,5):
      y = x*x - 15
  else:
      y = 10*random() + sin(2*pi*x/60)
  return round(10+y ,4)


app = Flask(__name__)

# Metrics
temperature = Gauge('monapp_position_in_stock', 'Position in stock (1000 tons)', ['position'])
temperature.labels('Rice').set_function(get_data)
temperature.labels('Corn').set_function(get_data2)
metrics = PrometheusMetrics(app, export_defaults=True)

# static information as metric
metrics.info('app_info', 'Application info', version='1.0.3')

@app.route('/')
def main():
    return 'main'

@app.route("/alert", methods=['POST'])
def alert():
    alert = request.get_json()
    print(alert)
    logger.fatal(f"{alert['commonAnnotations']['summary']}. Alert has been created")
    return dumps({'success':True}), 200, {'ContentType':'application/json'} 
    


@app.route('/data')
def data():
    data = get_data()
    return str(data)

from threading import Thread

def ram():
    logger.info("Starting RAM task")
    ['A'*1024 for _ in range(0, 1024*1024*1024)]
    logger.info("RAM task completed")


def cpu():
    logger.info("Starting CPU task")
    start_time = datetime.now()
    now = datetime.now()
    while (now - start_time).seconds < 30:
        pass
        now = datetime.now()
    logger.info(" CPU task completed")

@app.route('/cpu_task')
def cpu_task():
    thread = Thread(target=cpu)
    thread.daemon = True
    thread.start()
    return jsonify({'thread_name': str(thread.name),
                    'started': True})


@app.route('/ram_task')
def ram_task():
    thread = Thread(target=ram)
    thread.daemon = True
    thread.start()
    return jsonify({'thread_name': str(thread.name),
                    'started': True})


def scheduled_action():
    chance = randint(0, 19)
    message = ' '.join(Gibberish().generate_words(wordcount=3, vowel_consonant_repeats=1))
    if chance in (18, 19):
        logger.error(message)
    elif chance in (16, 17):
        logger.warning(message)
    else:
        logger.info(message)


scheduler = BackgroundScheduler()
scheduler.add_job(func=scheduled_action, trigger="interval", seconds=10)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)