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
    dbclient.create_retention_policy('60_days', '60d', 1, influx_database, default=False)
    dbclient.create_retention_policy('infinite', 'INF', 1, influx_database, default=False)

    print( dbclient.get_list_continuous_queries() )

    p1_select_clause = 'SELECT mean("+P") as "+P",mean("+P1") as "+P1",mean("+P2") as "+P2",mean("+P3") as "+P3",mean("+T") as "+T",mean("+T1") as "+T1",mean("+T2") as "+T2",mean("-P") as "-P",mean("-P1") as "-P1",mean("-P2") as "-P2",mean("-P3") as "-P3",mean("-T") as "-T",mean("-T1") as "-T1",mean("-T2") as "-T2",mean("G") as "G",mean("P") as "P"'
    dbclient.create_continuous_query("p1_mean10", p1_select_clause + ' INTO "10_days"."p1" FROM "p1" GROUP BY time(5m)', influx_database )
    dbclient.create_continuous_query("p1_mean60", p1_select_clause + ' INTO "60_days"."p1" FROM "p1" GROUP BY time(15m)', influx_database )
    dbclient.create_continuous_query("p1_meaninf", p1_select_clause + ' INTO "infinite"."p1" FROM "p1" GROUP BY time(30m)', influx_database )   
    
    solar_select_clause = 'SELECT mean("ac_frequency") as "ac_frequency",mean("ac_output_amps_1") as "ac_output_amps_1",mean("ac_output_amps_2") as "ac_output_amps_2",mean("ac_output_amps_3") as "ac_output_amps_3",mean("ac_output_volts_1") as "ac_output_volts_1",mean("ac_output_volts_2") as "ac_output_volts_2",mean("ac_output_volts_3") as "ac_output_volts_3",mean("current_generation_watts_1") as "current_generation_watts_1",mean("current_generation_watts_2") as "current_generation_watts_2",mean("current_generation_watts_3") as "current_generation_watts_3",mean("dc_amps_chain_1") as "dc_amps_chain_1",mean("dc_amps_chain_2") as "dc_amps_chain_2",mean("dc_amps_chain_3") as "dc_amps_chain_3",mean("dc_volts_chain_1") as "dc_volts_chain_1",mean("dc_volts_chain_2") as "dc_volts_chain_2",mean("dc_volts_chain_3") as "dc_volts_chain_3",mean("inverter_daily") as "inverter_daily",mean("inverter_last_month") as "inverter_last_month",mean("inverter_month") as "inverter_month",mean("inverter_total") as "inverter_total",mean("inverter_yesterday") as "inverter_yesterday",mean("temperature") as "temperature"'
    dbclient.create_continuous_query("solar_mean10", solar_select_clause + ' INTO "10_days"."solar" FROM "solar" GROUP BY time(5m)', influx_database )
    dbclient.create_continuous_query("solar_mean60", solar_select_clause + ' INTO "60_days"."solar" FROM "solar" GROUP BY time(15m)', influx_database )
    dbclient.create_continuous_query("solar_meaninf", solar_select_clause + ' INTO "infinite"."solar" FROM "solar" GROUP BY time(30m)', influx_database )

    weather_select_clause = 'SELECT mean("clouds") as "clouds",mean("detailed_status") as "detailed_status",mean("humidity") as "humidity",mean("lastrain") as "lastrain",mean("lastsnow") as "lastsnow",mean("location") as "location",mean("pressure") as "pressure",mean("status") as "status",mean("sunrise") as "sunrise",mean("sunset") as "sunset",mean("temp") as "temp",mean("weather_code") as "weather_code",mean("weather_icon") as "weather_icon",mean("wind_direction_deg") as "wind_direction_deg",mean("wind_speed") as "wind_speed"'
    dbclient.create_continuous_query("weather_mean10", weather_select_clause + ' INTO "10_days"."weather" FROM "weather" GROUP BY time(5m)', influx_database )
    dbclient.create_continuous_query("weather_mean60", weather_select_clause + ' INTO "60_days"."weather" FROM "weather" GROUP BY time(15m)', influx_database )
    dbclient.create_continuous_query("weather_meaninf", weather_select_clause + ' INTO "infinite"."weather" FROM "weather" GROUP BY time(30m)', influx_database )


    print( dbclient.get_list_continuous_queries() )

except Exception as e:
    print('Error querying open database: ' + influx_database)
    print(e)
