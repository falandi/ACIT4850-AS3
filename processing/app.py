import connexion
from connexion import NoContent
import datetime
import json
import logging
import logging.config
import requests
import yaml
# import apscheduler
# from apscheduler.schedulers.background import BackgroundScheduler

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from stats import Stats
import storage
from storage.app import buy
from storage.app import sell

DB_ENGINE = create_engine("sqlite:///stats.sqlite")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def get_latest_stats():
    # TODO create a session
    session = DB_SESSION()    

    # TODO query the session for the first Stats record, ordered by Stats.last_updated

    stats_query = session.query(Stats).order_by(Stats.last_updated).first()

    # TODO if result is not empty, convert it to a dict and return it (with status code 200)
    if stats_query != None:
        stats_query.to_dict()
        return stats_query, 200
    # TODO if result is empty, return NoContent, 201
    return NoContent, 201

def populate_stats():
    #   IMPORTANT: all stats calculated by populate_stats must be CUMULATIVE
    # 
    #   The number of buy and sell events received must be added to the previous total held in stats.sqlite,
    #   and the max_buy_price and max_sell_price must be compared to the values held in stats.sqlite
    #
    #   e.g. if the latest Stat in the sqlite db is:
    #   { 19.99, 10, 10.99, 5, 2023-01-01T00:00:00Z }  (max_buy_price, num_buys, max_sell_price, num_sells, timestamp)
    #
    #   and 4 new buy events are received with a max price of 99.99, the next stat written to stats must be similar to:
    #   { 99.99, 14, 10.99, 5, 2023-01-01T00:00:05Z }
    #
    #   if 10 more sell events were also received, but the max price of all events did not exceed 10.99, the stat would
    #   then look something like:
    #   { 99.99, 14, 10.99, 15, 2023-01-01T00:00:05Z }
    #


    # TODO create a timestamp (e.g. datetime.datetime.now().strftime('...'))
    timestamp =  datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

    # TODO create a last_updated variable that is initially assigned the timestamp, i.e. last_updated = timestamp
    last_updated = timestamp

    # TODO log beginning of processing
    logger.debug(f"Request started at time {last_updated}.")
    
    # TODO create a session
    session = DB_SESSION()   

    # TODO read latest record from stats.sqlite (ordered by last_updated)
    # e.g. result = session.query(Stats)...  etc.
    result = session.query(Stats).order_by(Stats.last_updated).first()
    # TODO if result is not empty, convert result to a dict, read the last_updated property and store it in a variable named last_updated
    # if result does not exist, create a dict with default keys and values, and store it in the result variable
    # if result != None:
    result = result.to_dict()
    last_updated = result['last_updated']

    # else:
        # result = {} 


    # TODO call the /buy GET endpoint of storage, passing last_updated
    rows = requests.get(f"http://localhost:8090/buy?timestamp={last_updated}")
    # TODO convert result to a json object, loop through and calculate max_buy_price of all recent records
  
    rows = rows.json()
    for item in rows:
        if item['buy_price'] > result['max_buy_price']:
            result['max_buy_price'] = item['buy_price']



    
    # TODO call the /sell GET endpoint of storage, passing last_updated
    sell_rows = requests.get(f"http://localhost:8090/sell?timestamp={last_updated}")

    # TODO convert result to a json object, loop through and calculate max_sell_price of all recent records
    sell_rows = sell_rows.json()
    for item in sell_rows:
        if item['sell_price'] > result['max_sell_price']:
            result['max_sell_price'] = item['sell_price']


    # TODO write a new Stats record to stats.sqlite using timestamp and the statistics you just generated
    ?????

    # TODO add, commit and optionally close the session
    session.add()
    session.commit()
    session.close()

    return NoContent, 201

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['period'])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basic')

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, use_reloader=False)
