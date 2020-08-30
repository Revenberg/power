#!/usr/bin/python3 -O

import os
import socket
import binascii
import time
import sys
import configparser
from influxdb import InfluxDBClient

config = configparser.RawConfigParser(allow_no_value=True)
config.read("weather_config.ini")

###########################
# Variables

do_raw_log = config.getboolean('Logging', 'do_raw_log')

influx_server = config.get('InfluxDB', 'influx_server')
influx_port = int(config.get('InfluxDB', 'influx_port'))
influx_database = config.get('InfluxDB', 'database')

if __debug__:
    print("running with debug")
    print(influx_server)
    print(influx_port)
    print(influx_database)
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
    dbclient.create_retention_policy('60_days', '60d', 1, influx_database, default=False)
    dbclient.create_retention_policy('infinite', 'INF', 1, influx_database, default=False)

    print( dbclient.get_list_continuous_queries() )

    weather_select_clause = 'SELECT mean("clouds") as "clouds",mean("detailed_status") as "detailed_status",mean("humidity") as "humidity",mean("lastrain") as "lastrain",mean("lastsnow") as "lastsnow",mean("location") as "location",mean("pressure") as "pressure",mean("status") as "status",mean("sunrise") as "sunrise",mean("sunset") as "sunset",mean("temp") as "temp",mean("weather_code") as "weather_code",mean("weather_icon") as "weather_icon",mean("wind_direction_deg") as "wind_direction_deg",mean("wind_speed") as "wind_speed"'
    dbclient.create_continuous_query("weather_mean60", weather_select_clause + ' INTO "60_days"."weather" FROM "weather" GROUP BY time(15m)', influx_database )
    dbclient.create_continuous_query("weather_meaninf", weather_select_clause + ' INTO "infinite"."weather" FROM "weather" GROUP BY time(30m)', influx_database )


    print( dbclient.get_list_continuous_queries() )

except Exception as e:
    print('Error querying open database: ' + influx_database)
    print(e)
