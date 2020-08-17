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

# What address to listen to (0.0.0.0 means it will listen on all addresses)
listen_address = config.get('DEFAULT', 'listen_address')
listen_port = int(config.get('DEFAULT', 'listen_port'))

log_path = config.get('Logging', 'log_path', fallback='/var/log/ginlong/')
do_raw_log = config.getboolean('Logging', 'do_raw_log')

influx_server = config.get('InfluxDB', 'influx_server')
influx_port = int(config.get('InfluxDB', 'influx_port'))
influx_database = config.get('InfluxDB', 'database')
influx_measurement = config.get('InfluxDB', 'measurement')

if __debug__:
    print("running with debug")
    print(listen_address)
    print(listen_port)
    print(influx_server)
    print(influx_port)
    print(influx_database)
    print(influx_measurement)
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
        logging.info('Database <%s> not found, trying to create it', influx_database)
        dbclient.create_database(influx_database)
        dbclient.create_retention_policy('30_days', '30d', 1, default=True)
        dbclient.create_retention_policy('6_months', '26wd', 1, default=False)
        dbclient.create_retention_policy('infinite', 'INF', 1, default=False)
    
except Exception as e:
    logging.error('Error querying open database: %s', e)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((listen_address, listen_port))
sock.listen(1)

conn, addr = sock.accept()

while True:
    # Wait for a connection
    if __debug__:
        print('waiting for a connection')
    try:
        print('connection from', addr)

        # Read in a chunk of data
        rawdata = conn.recv(512).strip()

        # Convert to hex for easier processing
        hexdata = binascii.hexlify(rawdata)

        timestamp = (time.strftime("%F %H:%M"))         # get date time

        if __debug__:
            print('Time: %s' % timestamp)
            print('Length: %s' % len(hexdata))
            print('Hex data: %s' % hexdata.decode())

        if do_raw_log:
            logfile = open(os.path.join(log_path, 'raw.log'), 'a')
            logfile.write(timestamp + ' ' + hexdata.decode() + '\n')
            logfile.close()

        if len(hexdata) >= 185:

            values = dict()
            print(str(hexdata[30:60]))
            # Serial number is used as InfluxDB tag,
            # allowing multiple inverters to connect to a single instance
#            serial = binascii.unhexlify(hexdata[30:60])
            print("====================")
            print(binascii.unhexlify(hexdata[30:60]))
#            serial = str(hexdata[30:60])
            serial = 1
            values['temperature'] = float(int(hexdata[62:66], 16))/10   # temperature
            values['dc_volts_chain_1'] = float(int(hexdata[66:70], 16))/10   # DC volts chain 1
            values['dc_volts_chain_2'] = float(int(hexdata[70:74], 16))/10   # DC volts chain 2
            values['dc_volts_chain_3'] = float(int(hexdata[74:78], 16))/10   # DC volts chain 3
            values['dc_amps_chain_1'] = float(int(hexdata[78:82], 16))/10   # DC amps chain 1
            values['dc_amps_chain_2'] = float(int(hexdata[82:86], 16))/10   # DC amps chain 2
            values['dc_amps_chain_3'] = float(int(hexdata[86:90], 16))/10   # DC amps chain 3
            values['ac_output_amps_1'] = float(int(hexdata[90:94], 16))/10   # AC output amps 1
            values['ac_output_amps_2'] = float(int(hexdata[94:98], 16))/10   # AC output amps 2
            values['ac_output_amps_3'] = float(int(hexdata[98:102], 16))/10  # AC output amps 3
            values['ac_output_volts_1'] = float(int(hexdata[102:106], 16))/10 # AC output volts 1
            values['ac_output_volts_2'] = float(int(hexdata[106:110], 16))/10 # AC output volts 2
            values['ac_output_volts_3'] = float(int(hexdata[110:114], 16))/10 # AC output volts 3
            values['ac_frequency'] = float(int(hexdata[114:118], 16))/100 # AC frequency
            values['current_generation_watts_1'] = float(int(hexdata[118:122], 16))    # current generation Watts 1
            values['current_generation_watts_2'] = float(int(hexdata[122:126], 16))    # current generation Watts 2
            values['current_generation_watts_3'] = float(int(hexdata[126:130], 16))    # current generation Watts 3
            #unknown = float(int(hexdata[130:134],16))/100
##            values['kwhtoday'] = float(int(hexdata[138:142], 16))/100
##            values['kwhyesterday'] = float(int(hexdata[134:138], 16))/100
##            values['kwhtotal'] = float(int(hexdata[142:150], 16))/10


            values['inverter_yesterday'] = float(int(hexdata[134:136], 16))/100  # yesterday kwh
            values['inverter_daily'] = float(int(hexdata[138:140], 16))/100      # daily kWh
            values['inverter_total'] = float(int(hexdata[142:148], 16))/10       # total kWh
            values['inverter_month'] = float(int(hexdata[174:176], 16))          # total kWh for month
            values['inverter_last_month'] = float(int(hexdata[182:184], 16))     # total kWh for last month

            print(values)

#            json_body = {'points': [{'tags': {'serial': serial.decode()},
            json_body = {'points': [{'tags': {'serial':  serial },
                                     'fields': {k: v for k, v in values.items()}
                                     }],
                         'measurement': influx_measurement
                         }
            print(json_body)

            print("Call InfluxDBClient")
            client = InfluxDBClient(host=influx_server,
                                    port=influx_port)
            success = client.write(json_body,
                                   # params isneeded, otherwise error 'database is required' happens
                                   params={'db': influx_database})

            if not success:
                print('error writing to database')

            client.close()

    except Exception as e:
        print(e)
        print("Unexpected error:", sys.exc_info()[0])
#        raise
    finally:
        if __debug__:
            print("Finally")
