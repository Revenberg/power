#!/usr/bin/python3 -O

import os
import socket
import binascii
import time
import sys
import configparser
from influxdb import InfluxDBClient

config = configparser.RawConfigParser(allow_no_value=True)
config.read("ginlong_config.ini")

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

    ginlong_select_clause = 'SELECT mean("AC_Current_S/V/B_[A]") as "AC_Current_S/V/B_[A]",mean("AC_Current_T/W/C_[A]") as "AC_Current_T/W/C_[A]",mean("AC_Output_Frequency_R_[Hz]") as "AC_Output_Frequency_R_[Hz]",mean("AC_Output_Total_Power_(Active)_[W]") as "AC_Output_Total_Power_(Active)_[W]",mean("AC_Voltage_R/U/A_[V]") as "AC_Voltage_R/U/A_[V]",mean("AC_Voltage_S/V/B_[V]") as "AC_Voltage_S/V/B_[V]",mean("AC_Voltage_T/W/C_[V]") as "AC_Voltage_T/W/C_[V]",mean("Annual_Generation_(Active)_[Wh]") as "Annual_Generation_(Active)_[Wh]",mean("DC_Current1_[A]") as "DC_Current1_[A]",mean("DC_Current2_[A]") as "DC_Current2_[A]",mean("DC_Power_PV1_[W]") as "DC_Power_PV1_[W]",mean("DC_Power_PV2_[W]") as "DC_Power_PV2_[W]",mean("DC_Voltage_PV1_[V]") as "DC_Voltage_PV1_[V]",mean("DC_Voltage_PV2_[V]") as "DC_Voltage_PV2_[V]",mean("Daily_Generation_(Active)_[Wh]") as "Daily_Generation_(Active)_[Wh]",mean("Generation_Yesterday_[Wh]") as "Generation_Yesterday_[Wh]",mean("Generation_of_Last_Month_(Active)_[Wh]") as "Generation_of_Last_Month_(Active)_[Wh]",mean("Monthly_Generation_(Active)_[Wh]") as "Monthly_Generation_(Active)_[Wh]",mean("Total_DC_Input_Power_[W]") as "Total_DC_Input_Power_[W]",mean("Total_Generation_(Active)_[Wh]") as "Total_Generation_(Active)_[Wh]"'

    dbclient.create_continuous_query("ginlong_mean60", ginlong_select_clause + ' INTO "60_days"."ginlong" FROM "ginlong" GROUP BY time(15m)', influx_database )
    dbclient.create_continuous_query("ginlong_meaninf", ginlong_select_clause + ' INTO "infinite"."ginlong" FROM "ginlong" GROUP BY time(30m)', influx_database )

    print( dbclient.get_list_continuous_queries() )

except Exception as e:
    print('Error querying open database: ' + influx_database)
    print(e)
