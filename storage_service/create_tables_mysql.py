import mysql.connector
import yaml

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

datastore = app_config["datastore"]

db_conn = mysql.connector.connect(host=datastore["hostname"], user=datastore["user"], password=datastore["password"],
                                  database=datastore["db"])
db_cursor = db_conn.cursor()


db_cursor.execute('''
 CREATE TABLE pickup
 (id INT NOT NULL AUTO_INCREMENT,
  order_id VARCHAR(250) NOT NULL,
  order_type VARCHAR(250) NOT NULL,
  orderer_id VARCHAR(250) NOT NULL,
  orderer_address VARCHAR(100) NOT NULL,
  distance_to_restaurant INTEGER NOT NULL,
  restaurant_id VARCHAR(250) NOT NULL,
  restaurant_address VARCHAR(100) NOT NULL,
  timestamp VARCHAR(100) NOT NULL,
  date_created VARCHAR(100) NOT NULL,
  CONSTRAINT pickup_order_pk PRIMARY KEY (id))
  ''')

db_cursor.execute('''
 CREATE TABLE delivery
 (id INT NOT NULL AUTO_INCREMENT,
 order_id VARCHAR(250) NOT NULL,
 order_type VARCHAR(250) NOT NULL,
 orderer_id VARCHAR(250) NOT NULL,
 orderer_address VARCHAR(100) NOT NULL,
 distance_to_restaurant INTEGER NOT NULL,
 restaurant_id VARCHAR(250) NOT NULL,
 restaurant_address VARCHAR(100) NOT NULL,
 timestamp VARCHAR(100) NOT NULL,
 date_created VARCHAR(100) NOT NULL,
 CONSTRAINT delivery_pk PRIMARY KEY (id))
 ''')

db_conn.commit()
db_conn.close()
