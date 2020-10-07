import sqlite3

conn = sqlite3.connect('orders.sqlite')

c = conn.cursor()
c.execute('''
          DROP TABLE pickup
          ''')
conn.commit()

c.execute('''
          DROP TABLE delivery
          ''')

conn.commit()
conn.close()
