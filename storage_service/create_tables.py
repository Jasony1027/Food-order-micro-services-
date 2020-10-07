import sqlite3

conn = sqlite3.connect('orders.sqlite')

c = conn.cursor()
c.execute('''
          CREATE TABLE pickup
          (id INTEGER PRIMARY KEY ASC, 
           order_id VARCHAR(250) NOT NULL,
           order_type VARCHAR(250) NOT NULL,
           orderer_id VARCHAR(250) NOT NULL,
           orderer_address VARCHAR(100) NOT NULL,
           distance_to_restaurant INTEGER NOT NULL,
           restaurant_id VARCHAR(250) NOT NULL,
           restaurant_address VARCHAR(100) NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL)
          ''')

c.execute('''
          CREATE TABLE delivery
          (id INTEGER PRIMARY KEY ASC, 
           order_id VARCHAR(250) NOT NULL,
           order_type VARCHAR(250) NOT NULL,
           orderer_id VARCHAR(250) NOT NULL,
           orderer_address VARCHAR(100) NOT NULL,
           distance_to_restaurant INTEGER NOT NULL,
           restaurant_id VARCHAR(250) NOT NULL,
           restaurant_address VARCHAR(100) NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL)
          ''')

conn.commit()
conn.close()
