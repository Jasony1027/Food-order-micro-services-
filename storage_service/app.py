import connexion
import yaml
import logging
import logging.config
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from pickup_order import PickupOrder
from delivery_order import DeliveryOrder


with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
datastore = app_config["datastore"]

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

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

    return NoContent, 201


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
    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", base_path='/', strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8090)
