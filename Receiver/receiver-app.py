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

    logger.debug(f'Received {endpoint} event with trace id {trace_id}')

    client = KafkaClient(hosts= "http://localhost:29092")

    topic = client.topics['events']

    producer = topic.get_sync_producer()
    

    my_dict = {
        "type":  endpoint, 
        "daytime": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'), 
        "payload": event

    }


    to_json = json.dumps(my_dict)
    producer.produce(to_json.encode('utf-8'))
    logger.debug(f"PRODUCER::producing {event} event")
    logger.debug(to_json)

    return NoContent, 201

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
