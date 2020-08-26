#!/usr/bin/python3 -O

import os
import socket
import binascii
import time
import sys
import configparser
from influxdb import InfluxDBClient

config = configparser.RawConfigParser(allow_no_value=True)
config.read("config.ini")

###########################
# Variables

log_path = config.get('Logging', 'log_path', fallback='/var/log/solar/')
do_raw_log = config.getboolean('Logging', 'do_raw_log')

influx_server = config.get('InfluxDB', 'influx_server')
influx_port = int(config.get('InfluxDB', 'influx_port'))
influx_database = config.get('InfluxDB', 'database')

if __debug__:
    print("running with debug")
    print(influx_server)
    print(influx_port)
    print(influx_database)
    print(log_path)
    print(do_raw_log)
else:
    print("running without debug")

# if the db is not found, then try to create it
try:
    dbclient = InfluxDBClient(host=influx_server, port=influx_port)
    dblist = dbclient.get_list_database()
    db_found = False
    for db in dblist:
        if db['name'] == influx_database:
            db_found = True
    if not(db_found):
        print('Database ' + influx_database + ' not found, trying to create it')
        dbclient.create_database(influx_database)

    dbclient.create_retention_policy('10_days', '10d', 1, influx_database, default=True)
    dbclient.create_retention_policy('30_days', '30d', 1, influx_database, default=False)
    dbclient.create_retention_policy('6_months', '26w', 1, influx_database, default=False)
    dbclient.create_retention_policy('infinite', 'INF', 1, influx_database, default=False)

    print( dbclient.get_list_continuous_queries() )

    select_clause = 'SELECT mean("+P") as "+P",mean("+P1") as "+P1",mean("+P2") as "+P2",mean("+P3") as "+P3",mean("+T") as "+T",mean("+T1") as "+T1",mean("+T2") as "+T2",mean("-P") as "-P",mean("-P1") as "-P1",mean("-P2") as "-P2",mean("-P3") as "-P3",mean("-T") as "-T",mean("-T1") as "-T1",mean("-T2") as "-T2",mean("G") as "G",mean("P") as "P" INTO "30_days"."p1_mean" FROM "p1" GROUP BY time(5m)'

    dbclient.create_continuous_query("p1_mean", select_clause, influx_database )

    print( dbclient.get_list_continuous_queries() )

except Exception as e:
    print('Error querying open database: ' + influx_database)
    print(e)
