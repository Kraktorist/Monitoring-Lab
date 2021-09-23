import atexit
import logging
import sys


from datetime import datetime
from json import dumps
from random import randint
from threading import Thread
from flask import escape, Flask, request, jsonify
from gibberish import Gibberish

from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Gauge
from apscheduler.schedulers.background import BackgroundScheduler

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

logger = logging.getLogger('monapp')
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',  datefmt='%a, %d %b %Y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)


def seconds_since_midnight():
    now = datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return (now - midnight).seconds


def get_rice():
    if app.grow['rice']:
        app.rice = app.rice + 1
    else:
        app.rice = app.rice - 1
    if app.rice < 0:
        app.rice = 0
    return app.rice


def get_corn():
    if app.grow['corn']:
        app.corn = app.corn + 2
    else:
        app.corn = app.corn - 4
    if app.corn < 0:
        app.corn = 0
    return app.corn


app = Flask(__name__)
# variable for changing graph
app.grow = {'corn': True, 'rice': True}
app.rice = 0
app.corn = 0

# Metrics
temperature = Gauge('monapp_position_in_stock',
                    'Position in stock (1000 tons)', ['position'])
temperature.labels('Corn').set_function(get_corn)
temperature.labels('Rice').set_function(get_rice)
metrics = PrometheusMetrics(app, export_defaults=True)

# static information as metric
metrics.info('app_info', 'Application info', version='1.0.3')


@app.route('/')
def main():
    """Main page"""
    result = """
        <h3>Management interfaces</h3>
        <i>Possible addresses</i> <br>
        <a href="http://localhost:3000"> http://localhost:3000 </a> 
        Grafana <br>
        <a href="http://localhost:5601"> http://localhost:5601 </a> 
        Kibana <br>
        <a href="http://localhost:8080"> http://localhost:8080 </a> 
        cAdvisor <br>
        <a href="http://localhost:9200"> http://localhost:9200 </a> 
        Elasticsearch <br>
        <a href="http://localhost:9090"> http://localhost:9090 </a> 
        Prometheus <br>
        <a href="http://localhost:9093"> http://localhost:9093 </a> 
        Alertmanager <br>
    """
    result += "<h3>Available methods</h3>"
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            result += f'''
            <a href="{rule.rule}"> { escape(rule.rule) } </a> 
            {app.view_functions[rule.endpoint].__doc__} <br>'''
    return result


@app.route('/switch/<grain>')
def switch(grain):
    """Order to start/stop loading grain"""
    if grain in ['rice', 'corn']:
        app.grow[grain] = not app.grow[grain]
        return f'{grain} START!' if app.grow[grain] else f'{grain} STOP!'
    else:
        return 'grain is not specified'


@app.route("/alert", methods=['POST'])
def alert():
    """Creates an alert"""
    message = request.get_json()
    print(message)
    logger.fatal("%s. Alert has been created", {message['commonAnnotations']['summary']})
    return dumps({'success': True}), 200, {'ContentType': 'application/json'}


def ram():
    """RAM test"""
    logger.info("Starting RAM task")
    ['A'*1024 for _ in range(0, 1024*1024*1024)]  # nopep8
    logger.info("RAM task completed")


def cpu():
    """CPU test"""
    logger.info("Starting CPU task")
    start_time = datetime.now()
    now = datetime.now()
    while (now - start_time).seconds < 30:
        now = datetime.now()
    logger.info(" CPU task completed")


@app.route('/cpu_task')
def cpu_task():
    """CPU test handler"""
    thread = Thread(target=cpu)
    thread.daemon = True
    thread.start()
    return jsonify({'thread_name': str(thread.name),
                    'started': True})


@app.route('/ram_task')
def ram_task():
    """RAM test handler"""
    thread = Thread(target=ram)
    thread.daemon = True
    thread.start()
    return jsonify({'thread_name': str(thread.name),
                    'started': True})


def scheduled_action():
    """Log messages generator"""
    chance = randint(0, 19)
    message = ' '.join(Gibberish().generate_words(
        wordcount=3, vowel_consonant_repeats=1))
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
