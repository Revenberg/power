#!/usr/bin/python3 -O

import os
import socket
import binascii
import time
import sys
import configparser
from influxdb import InfluxDBClient

config = configparser.RawConfigParser(allow_no_value=True)
config.read("rs485_config.ini")

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

    rs485_select_clause = 'SELECT mean("AC Current 1 (A)") as "AC Current 1 (A)",mean("AC Current 2 (A)") as "AC Current 2 (A)",mean("AC Current 3 (A)") as "AC Current 3 (A)",mean("AC Frequency (Hz)") as "AC Frequency (Hz)",mean("AC Watts (W)") as "AC Watts (W)",mean("AC voltage 1 (V)") as "AC voltage 1 (V)",mean("AC voltage 2 (V)") as "AC voltage 2 (V)",mean("AC voltage 3 (V)") as "AC voltage 3 (V)",mean("DC Current 1 (A)") as "DC Current 1 (A)",mean("DC Current 2 (A)") as "DC Current 2 (A)",mean("DC Voltage 1 (V)") as "DC Voltage 1 (V)",mean("DC Voltage 2 (V)") as "DC Voltage 2 (V)",mean("Generated (All time)") as "Generated (All time)",mean("Generated (Today)") as "Generated (Today)",mean("Inverter Temperature (c)") as "Inverter Temperature (c)",mean("Last month energy (W)") as "Last month energy (W)",mean("Last year energy") as "Last year energy",mean("Month energy (W)") as "Month energy (W)",mean("Total energy (W)") as "Total energy (W)",mean("ac power (A)") as "ac power (A)",mean("pv power (V)") as "pv power (V)"'
    dbclient.create_continuous_query("rs485_mean60", rs485_select_clause + ' INTO "60_days"."rs485" GROUP BY time(15m)', influx_database )
    dbclient.create_continuous_query("rs485_meaninf", rs485_select_clause + ' INTO "infinite"."rs485" FROM "rs485" GROUP BY time(30m)', influx_database )

    print( dbclient.get_list_continuous_queries() )

except Exception as e:
    print('Error querying open database: ' + influx_database)
    print(e)
