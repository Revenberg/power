#!/usr/bin/python3 -O

import os
import socket
import binascii
import time
import sys
import configparser
from influxdb import InfluxDBClient

config = configparser.RawConfigParser(allow_no_value=True)
config.read("rs385_config.ini")

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

#    rs385_select_clause = 'SELECT mean("ac_frequency") as "ac_frequency",mean("ac_output_amps_1") as "ac_output_amps_1",mean("ac_output_amps_2") as "ac_output_amps_2",mean("ac_output_amps_3") as "ac_output_amps_3",mean("ac_output_volts_1") as "ac_output_volts_1",mean("ac_output_volts_2") as "ac_output_volts_2",mean("ac_output_volts_3") as "ac_output_volts_3",mean("current_generation_watts_1") as "current_generation_watts_1",mean("current_generation_watts_2") as "current_generation_watts_2",mean("current_generation_watts_3") as "current_generation_watts_3",mean("dc_amps_chain_1") as "dc_amps_chain_1",mean("dc_amps_chain_2") as "dc_amps_chain_2",mean("dc_amps_chain_3") as "dc_amps_chain_3",mean("dc_volts_chain_1") as "dc_volts_chain_1",mean("dc_volts_chain_2") as "dc_volts_chain_2",mean("dc_volts_chain_3") as "dc_volts_chain_3",mean("inverter_daily") as "inverter_daily",mean("inverter_last_month") as "inverter_last_month",mean("inverter_month") as "inverter_month",mean("inverter_total") as "inverter_total",mean("inverter_yesterday") as "inverter_yesterday",mean("temperature") as "temperature"'
#    dbclient.create_continuous_query("rs385_mean60", rs385_select_clause + ' INTO "60_days"."rs385" FROM "rs385" GROUP BY time(15m)', influx_database )
#    dbclient.create_continuous_query("rs385_meaninf", rs385_select_clause + ' INTO "infinite"."rs385" FROM "rs385" GROUP BY time(30m)', influx_database )

    print( dbclient.get_list_continuous_queries() )

except Exception as e:
    print('Error querying open database: ' + influx_database)
    print(e)
