import connexion
from connexion import NoContent
import json
import os.path
import requests
import datetime
from pykafka import KafkaClient
import yaml
import logging
import logging.config

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())


LOGGER = logging.getLogger('basicLogger')
HOSTNAME = "{}:{}".format(app_config["events"]["hostname"], app_config["events"]["port"])
TOPIC = app_config["events"]["topic"]


def get_pickup_order(index):
    """ processes received pickup order data"""
    client = KafkaClient(hosts=HOSTNAME)
    topic = client.topics[TOPIC]
    # Here we reset the offset on start so that we retrieve messages
    # at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to 100ms.
    # There is a risk that this loop never stops if
    # the index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=100)
    LOGGER.info("Retrieving pickup at index {}".format(index))
    count = 0
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        if msg["type"] == "pickup":
            if count == index:
                # Find the event at the index you want and return code 200
                return msg["payload"], 200
            count += 1
    LOGGER.error("Could not find pickup at index %d" % index)
    return {"message": "Not Found"}, 404


def get_delivery_order(index):
    """ processes received pickup order data"""
    client = KafkaClient(hosts=HOSTNAME)
    topic = client.topics[TOPIC]
    # Here we reset the offset on start so that we retrieve messages
    # at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to 100ms.
    # There is a risk that this loop never stops if
    # the index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=100)
    LOGGER.info("Retrieving delivery at index {}".format(index))
    count = 0
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        if msg["type"] == "delivery":
            if count == index:
                # Find the event at the index you want and return code 200
                return msg["payload"], 200
            count += 1
    LOGGER.error("Could not find delivery at index %d" % index)
    return {"message": "Not Found"}, 404


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", base_path='/', strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8110)



