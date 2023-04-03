import datetime
import json
import connexion
from connexion import NoContent
import swagger_ui_bundle

import mysql.connector 
import pymysql
import yaml
import logging
import logging.config

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from buy import Buy
from sell import Sell
from pykafka import KafkaClient
from threading import Thread

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

# TODO: create connection string, replacing placeholders below with variables defined in log_conf.yml
DB_ENGINE = create_engine(f"mysql+pymysql://{app_config['user']}:{app_config['password']}@{app_config['hostname']}:{app_config['port']}/{app_config['db']}")

Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def process_messages():
    client = KafkaClient(
        hosts = "kafka:9092"
    )
    
    topic = client.topics['events']
    
    messages = topic.get_simple_consumer(
        consumer_group = b'event_group', 
        reset_offset_on_start = False, 
        auto_offset_reset = OffsetType.LATEST
    )

    for msg in messages:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        payload = msg["payload"]
        msg_type = msg["type"]

        session = DB_SESSION()

        logger.debug("CONSUMER::storing buy event")
        logger.debug(msg)

        if msg_type == 'buy':
            r = Buy(
                payload['buy_id'],
                msg['payload']['item_name'],
                msg['payload']['item_price'],
                msg['payload']['buy_qty'],
                msg['payload']['trace_id'],
            )
        else:
            r = Sell(
                msg['payload']['sell_id'],
                msg['payload']['item_name'],
                msg['payload']['item_price'],
                msg['payload']['sell_qty'],
                msg['payload']['trace_id']
            )

        session.add(r)
        session.commit()

    session.close()

    messages.commit_offsets()



# Endpoints
def buy(body):
    # TODO create a session
    session = DB_SESSION()
    # with session as session:
    buy_1 = Buy(
        body['buy_id'],
        body['item_name'],
        body['item_price'], 
        body['buy_qty'],
        body['trace_id']
    )
    session.add(buy_1)
    session.commit()
    # session.close()
    
    # TODO additionally pass trace_id (along with properties from Lab 2) into Buy constructor

    # TODO add, commit, and close the session

    # TODO: call logger.debug and pass in message "Stored buy event with trace id <trace_id>"
    logger.debug(f"Stored buy evetn with trace id { body['trace_id']}.") 
    

    # TODO return NoContent, 201
    return NoContent, 201
# end

def get_buys():
    # placeholder for future labs
    pass

def sell(body):
    session = DB_SESSION()
    # TODO create a session
    with session as session:
        sell_1 = Sell(
            body['sell_id'],
            body['item_name',
            body['item_price'], 
            body['sell_qty']],
            body['trace_id'])
        session.add(sell_1)
        session.commit()
        session.close()

        logger.debug(f"Stored sell event with trace id {body['trace_id']}.") 

    

    # TODO additionally pass trace_id (along with properties from Lab 2) into Sell constructor

    # TODO add, commit, and close the session

    # TODO: call logger.debug and pass in message "Stored buy event with trace id <trace_id>"

    return NoContent, 201
# end

def get_sells():
    # placeholder for future labs
    pass

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api('openapi.yaml', strict_validation=True, validate_responses=True)

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basic')

if __name__ == "__main__":
    tl = Thread(target=process_messages)
    tl.daemon = True
    tl.start()
    app.run(port=8090)