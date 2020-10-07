from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class DeliveryOrder(Base):

    __tablename__ = "delivery"

    id = Column(Integer, primary_key=True)
    order_id = Column(String(250), nullable=False)
    order_type = Column(String(250), nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)
    orderer_id = Column(String(250), nullable=False)
    orderer_address = Column(String(100), nullable=False)
    distance_to_restaurant = Column(Integer, nullable=False)
    restaurant_id = Column(String(250), nullable=False)
    restaurant_address = Column(String(100), nullable=False)

    def __init__(self, order_id, order_type, orderer_id, orderer_address, distance_to_restaurant,
                 restaurant_id, restaurant_address, timestamp):
        """ Initializes a delivery order """
        self.order_id = order_id
        self.order_type = order_type
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.orderer_id = orderer_id
        self.orderer_address = orderer_address
        self.distance_to_restaurant = distance_to_restaurant
        self.restaurant_id = restaurant_id
        self.restaurant_address = restaurant_address

    def to_dict(self):
        """ Dictionary Representation of a delivery order """
        dict = {}
        dict['id'] = self.id
        dict['order_id'] = self.order_id
        dict['order_type'] = self.order_type
        dict['orderer'] = {}
        dict['orderer']['orderer_id'] = self.orderer_id
        dict['orderer']['orderer_address'] = self.orderer_address
        dict['orderer']['distance_to_restaurant'] = self.distance_to_restaurant
        dict['restaurant'] = {}
        dict['restaurant']['restaurant_id'] = self.restaurant_id
        dict['restaurant']['restaurant_address'] = self.restaurant_address
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created

        return dict
