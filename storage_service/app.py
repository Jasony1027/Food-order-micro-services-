import connexion
import yaml
import json
import logging
import logging.config
import datetime
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from pickup_order import PickupOrder
from delivery_order import DeliveryOrder
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
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
    datastore = app_config["datastore"]
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


HOSTNAME = "{}:{}".format(app_config["events"]["hostname"], app_config["events"]["port"])
TOPIC = app_config["events"]["topic"]
# SQLite
# DB_ENGINE = create_engine("sqlite:///orders.sqlite")

# MySQL
DB_ENGINE = create_engine("mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
                          .format(user=datastore["user"],
                                  password=datastore["password"],
                                  port=datastore["port"],
                                  host=datastore["hostname"],
                                  database=datastore["db"]
                                  ))

Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)
logger.info("Connected to DB. Hostname: {}, Port: {}".format(datastore["hostname"], datastore["port"]))


def get_pickup_orders(timestamp):
    """ Gets new blood pressure readings after the timestamp """
    session = DB_SESSION()
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    print(timestamp_datetime)
    pickup_orders = session.query(PickupOrder).filter(PickupOrder.date_created >= timestamp_datetime)
    orders_list = []
    for order in pickup_orders:
        orders_list.append(order.to_dict())
    session.close()

    logger.info("Query for pickup order after {} returns {} results".format(timestamp, len(orders_list)))
    return orders_list, 200


def get_delivery_orders(timestamp):
    """ Gets new blood pressure readings after the timestamp """
    session = DB_SESSION()
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    delivery_orders = session.query(DeliveryOrder).filter(DeliveryOrder.date_created >= timestamp_datetime)
    orders_list = []
    for order in delivery_orders:
        orders_list.append(order.to_dict())
    session.close()

    logger.info("Query for pickup order after {} returns {} results".format(timestamp, len(orders_list)))
    return orders_list, 200


def store_pickup_order(body):
    """ Stores pick up order details to database """
    session = DB_SESSION()

    pickup = PickupOrder(body['order_id'],
                         body['order_type'],
                         body['orderer']['orderer_id'],
                         body['orderer']['orderer_address'],
                         body['orderer']['distance_to_restaurant'],
                         body['restaurant']['restaurant_id'],
                         body['restaurant']['restaurant_address'],
                         body['timestamp'])

    session.add(pickup)

    session.commit()
    session.close()
    logger.debug("Stored event '{}' request with a unique id of {}".format(body["order_type"], body["order_id"]))


def store_delivery_order(body):
    """ Stores delivery order details to database """
    session = DB_SESSION()

    delivery = DeliveryOrder(body['order_id'],
                             body['order_type'],
                             body['orderer']['orderer_id'],
                             body['orderer']['orderer_address'],
                             body['orderer']['distance_to_restaurant'],
                             body['restaurant']['restaurant_id'],
                             body['restaurant']['restaurant_address'],
                             body['timestamp'])

    session.add(delivery)

    session.commit()
    session.close()
    logger.debug("Stored event '{}' request with a unique id of {}".format(body["order_type"], body["order_id"]))


def process_messages():
    """ Process event messages """
    client = KafkaClient(hosts=HOSTNAME)
    topic = client.topics[TOPIC]

    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group='event_group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)
    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: {}".format(msg))
        payload = msg["payload"]
        if msg["type"] == "pickup":  # Change this to your event type
            # Store the event1 (i.e., the payload) to the DB
            store_pickup_order(payload)
        elif msg["type"] == "delivery":  # Change this to your event type
            # Store the event2 (i.e., the payload) to the DB
            store_delivery_order(payload)

        # Commit the new message as being read
        consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", base_path='/', strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)
