import connexion
from connexion import NoContent
import datetime
import json
import logging
import logging.config
import pykafka
from pykafka import KafkaClient
import requests
import uuid
import yaml 

def process_event(event, endpoint):
    trace_id = str(uuid.uuid4())
    event['trace_id'] = trace_id

    # TODO: call logger.debug and pass in message "Received event <type> with trace id <trace_id>"
    logger.debug(f"Received event {endpoint} with trace id {trace_id}")

    # headers = { 'Content-Type': 'application/json' }

    # TODO: update requests.post to use app_config property instead of hard-coded URL
    client = KafkaClient(
        hosts="kafka:9092", socket_timeout_ms=100000
    )


    topic = client.topics['events']
    producer = topic.get_sync_producer()

    msg = {
        "type": endpoint,
        "datetime": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
        "payload": event
    }
    msg_str = json.dumps(msg)

    producer.produce(msg_str.encode('utf-8'))

    logger.debug(f"PRODUCER::producing {endpoint} event")
    logger.debug(msg)

    return NoContent, 201

    # TODO: call logger.debug and pass in message "Received response with trace id <trace_id>, status code <status_code>"
    #logger.debug(f"Received response with trace id {trace_id}, status code {res.status_code}")

    # pass
    # # return res.text, res.status_code

# Endpoints
def buy(body):
    process_event(body, 'buy')
    return NoContent, 201

def sell(body):
    process_event(body, 'sell')
    return NoContent, 201

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basic')

if __name__ == "__main__":
    app.run(port=8080)