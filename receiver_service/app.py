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
import os

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())
# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger('basicLogger')
    logger.info("App Conf File: %s" % app_conf_file)
    logger.info("Log Conf File: %s" % log_conf_file)
with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)


MAX_EVENTS = 10
EVENTS_LOG = "events.json"
BASE_URL = "http://localhost:8090/orders/"
HOSTNAME = "{}:{}".format(app_config["events"]["hostname"], app_config["events"]["port"])
TOPIC = app_config["events"]["topic"]


def send_post_request(data, order_type):
    """ sends post request to storage service"""
    url = app_config[order_type]["url"]
    headers = {"content-type": "application/json"}
    response = requests.post(url, json=data, headers=headers)
    return response.status_code


def store_pickup_order(body):
    """ processes received pickup order data"""
    logger.info("Received event '{}' request with a unique id of {}".format(body["order_type"], body["order_id"]))
    client = KafkaClient(hosts=HOSTNAME)
    topic = client.topics[TOPIC]
    producer = topic.get_sync_producer()
    msg = {"type": "pickup",
           "datetime":
               datetime.datetime.now().strftime(
                   "%Y-%m-%dT%H:%M:%S"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    logger.info("Processed event '{}' request with a unique id of {}".format(body["order_type"], body["order_id"]))
    return NoContent, 201


def store_delivery_order(body):
    """ processes received delivery order data"""
    logger.info("Received event '{}' request with a unique id of {}".format(body["order_type"], body["order_id"]))
    client = KafkaClient(hosts=HOSTNAME)
    topic = client.topics[TOPIC]
    producer = topic.get_sync_producer()
    msg = {"type": "delivery",
           "datetime":
               datetime.datetime.now().strftime(
                   "%Y-%m-%dT%H:%M:%S"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    logger.info("Processed event '{}' request with a unique id of {}".format(body["order_type"], body["order_id"]))
    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", base_path='/receiver', strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)



