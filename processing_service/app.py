import connexion
from connexion import NoContent
import json
import os.path
import requests
import datetime
import yaml
import logging
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS, cross_origin
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
    filename = app_config["datastore"]["filename"]
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

MAX_DISTANCE = 100

default_data = {"num_orders": 0,
                "num_pickup_orders": 0,
                "num_delivery_orders": 0,
                "max_pickup_distance": "No data",
                "max_delivery_distance": "No data",
                "min_pickup_distance": "No data",
                "min_delivery_distance": "No data",
                "timestamp_pickup": "2020-11-04T00:00:00Z",
                "timestamp_delivery": "2020-11-04T00:00:00Z"
                }


def send_get_request(order_type, timestamp):
    url = app_config["eventstore"][order_type]["url"]
    headers = {"content-type": "application/json"}
    response = requests.get(url, params={"timestamp": timestamp}, headers=headers)
    return json.loads(response.content.decode('utf-8'))


def get_max(orders, idx, max):
    if idx == len(orders):
        return max
    if max == "No data":
        max = 0
        return get_max(orders, idx, max)
    elif orders[idx]["orderer"]["distance_to_restaurant"] >= max:
        max = orders[idx]["orderer"]["distance_to_restaurant"]
    return get_max(orders, idx+1, max)


def get_min(orders, idx, min):
    if idx == len(orders):
        return min
    if min == "No data":
        min = 100
        return get_min(orders, idx, min)
    elif orders[idx]["orderer"]["distance_to_restaurant"] <= min:
        min = orders[idx]["orderer"]["distance_to_restaurant"]
    return get_min(orders, idx+1, min)


def update_current_stats(pickup_orders, delivery_orders, stats):
    stats["num_orders"] += len(pickup_orders) + len(delivery_orders)
    now = datetime.datetime.now()
    now_str = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    stats["timestamp_pickup"] = now_str
    stats["timestamp_delivery"] = now_str
    if len(pickup_orders) != 0:
        stats["num_pickup_orders"] += len(pickup_orders)
        stats["max_pickup_distance"] = get_max(pickup_orders, 0, stats["max_pickup_distance"])
        stats["min_pickup_distance"] = get_min(pickup_orders, 0, stats["min_pickup_distance"])

    if len(delivery_orders) != 0:
        stats["num_delivery_orders"] += len(delivery_orders)
        stats["max_delivery_distance"] = get_max(delivery_orders, 0, stats["max_delivery_distance"])
        stats["min_delivery_distance"] = get_min(delivery_orders, 0, stats["min_delivery_distance"])

    logger.debug("Updated statistics: {}".format(stats))
    return stats


def get_stats():
    logger.info("Retrieving Statistics...")
    if not os.path.isfile(filename):
        logger.error("Error: Statistics do not exist")
        return "Statistics do not exist", 404
    with open(filename, "r") as f:
        current_stats = json.load(f)
        logger.info("Retrieved statistic: {}".format(current_stats))
        f.close()
    logger.info("Done")
    return current_stats, 200


def populate_stats():
    """ Periodically update stats """
    logger.info("Processing data...")
    if os.path.isfile(filename):
        with open(filename, "r") as f:
            current_stats = json.load(f)
            f.close()
    else:
        current_stats = default_data
        with open(filename, "w") as f:
            json.dump(current_stats, f, indent=4)
            f.close()
        return

    last_pickup_request_time = current_stats["timestamp_pickup"]
    last_delivery_request_time = current_stats["timestamp_delivery"]
    pickup_orders = send_get_request("pickup", last_pickup_request_time)
    logger.info("Received {} pickup orders".format(len(pickup_orders)))
    delivery_orders = send_get_request("delivery", last_delivery_request_time)
    logger.info("Received {} delivery orders".format(len(delivery_orders)))

    current_stats = update_current_stats(pickup_orders, delivery_orders, current_stats)
    with open(filename, "w") as f:
        json.dump(current_stats, f, indent=4)
        f.close()
    logger.info("Done")


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yml", base_path='/', strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100)



