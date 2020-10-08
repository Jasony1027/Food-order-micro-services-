import connexion
from connexion import NoContent
import json
import os.path
import requests
import yaml
import logging
import logging.config

MAX_EVENTS = 10
EVENTS_LOG = "events.json"
BASE_URL = "http://localhost:8090/orders/"


# def write_to_log(body):
# """ writes log messages to a json file"""
#     post_request_msgs = []
#     if os.path.isfile(EVENTS_LOG):
#         log = open(EVENTS_LOG, "r")
#         post_request_msgs = json.loads(log.read())
#         if len(post_request_msgs) >= MAX_EVENTS:
#             post_request_msgs.pop(0)
#     post_request_msgs.append(body)
#     log = open(EVENTS_LOG, "w")
#     log.write(json.dumps(post_request_msgs, indent=4))

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())


def send_post_request(data):
    url = app_config[data["order_type"]]["url"]
    headers = {"content-type": "application/json"}
    response = requests.post(url, json=data, headers=headers)
    return response.status_code


def store_pickup_order(body):
    logger.info("Received event '{}' request with a unique id of {}".format(body["order_type"], body["order_id"]))
    status_code = send_post_request(body)
    logger.info("Processed event '{}' request with a unique id of {}".format(body["order_type"], body["order_id"]))
    return NoContent, status_code


def store_delivery_order(body):
    logger.info("Received event '{}' request with a unique id of {}".format(body["order_type"], body["order_id"]))
    status_code = send_post_request(body)
    logger.info("Processed event '{}' request with a unique id of {}".format(body["order_type"], body["order_id"]))
    return NoContent, status_code


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", base_path='/', strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)



