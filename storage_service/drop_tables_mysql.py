import mysql.connector
import yaml

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

datastore = app_config["datastore"]

db_conn = mysql.connector.connect(host=datastore["hostname"], user=datastore["user"], password=datastore["password"],
                                  database=datastore["db"])
db_cursor = db_conn.cursor()
db_cursor.execute('''
 DROP TABLE pickup, delivery
''')
db_conn.commit()
db_conn.close()