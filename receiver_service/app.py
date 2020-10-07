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


def load_config_file():
    # loads app configuration file
    with open('app_conf.yml', 'r') as f:
        app_config = yaml.safe_load(f.read())
    return app_config


def log_to_file(data):
    # set up logger with log configuration file to log events output
    with open('log_conf.yml', 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)
    logger = logging.getLogger('basicLogger')
    logger.info("Received event '{}' request with a unique id of {}".format(data["order_type"], data["order_id"]))


def send_post_request(data):
    # sends POST requests to the storage service
    app_config_file = load_config_file()
    url = app_config_file[data["order_type"]]["url"]
    headers = {"content-type": "application/json"}
    response = requests.post(url, json=data, headers=headers)
    return response.status_code


def store_pickup_order(body):
    # sends pick up order details to storage service
    status_code = send_post_request(body)
    log_to_file(body)
    return NoContent, status_code


def store_delivery_order(body):
    # sends delivery order details to storage service
    status_code = send_post_request(body)
    log_to_file(body)
    return NoContent, status_code


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", base_path='/', strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)



