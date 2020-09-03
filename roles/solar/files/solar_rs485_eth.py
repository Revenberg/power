import rs485eth
import socket
import serial
import pyowm
import os
import binascii
import time
import sys
import configparser
import json
from influxdb import InfluxDBClient

config = configparser.RawConfigParser(allow_no_value=True)
config.read("rs485_config.ini")

log_path = config.get('Logging', 'log_path', fallback='/var/log/solar/')
do_raw_log = config.getboolean('Logging', 'do_raw_log')

server = config.get('rs485', 'server')
port = int(config.get('rs485', 'port'))

influx_server = config.get('InfluxDB', 'influx_server')
influx_port = int(config.get('InfluxDB', 'influx_port'))
influx_database = config.get('InfluxDB', 'database')
influx_measurement = config.get('InfluxDB', 'measurement')

if __debug__:
    print("running with debug")
    print(influx_server)
    print(influx_port)
    print(influx_database)
    print(influx_measurement)

    print(server)
    print(port)

    print(log_path)
    print(do_raw_log)
else:
    print("running without debug")


def getData():

    instrument = rs485eth.Instrument(server, port, 1, debug=False) # port name, slave address

    values = dict()
    values['Generated (All time)'] = instrument.read_long(3008, functioncode=4, signed=False) # Read All Time Energy (KWH Total) as Unsigned 32-Bit
    values['Generated (Today)'] = instrument.read_register(3014, numberOfDecimals=0, functioncode=4, signed=False) # Read Today Energy (KWH Total) as 16-Bit
    values['AC Watts (W)'] = instrument.read_long(3004, functioncode=4, signed=False) #Read AC Watts as Unsigned 32-Bit
    values['DC Voltage 1 (V)'] = instrument.read_register(3021, functioncode=4, signed=False) #Read DC Volts as Unsigned 16-Bit
    values['DC Current 1 (A)'] = instrument.read_register(3022, functioncode=4, signed=False) / 10 #Read DC Current as Unsigned 16-Bit
    values['DC Voltage 2 (V)'] = instrument.read_register(3023, functioncode=4, signed=False) / 10 #Read DC Volts as Unsigned 16-Bit
    values['DC Current 2 (A)'] = instrument.read_register(3024, functioncode=4, signed=False) / 10 #Read DC Current as Unsigned 16-Bit
    values['AC voltage 1 (V)'] = instrument.read_register(3033, functioncode=4, signed=False) / 10 #Read AC Volts as Unsigned 16-Bit
    values['AC voltage 2 (V)'] = instrument.read_register(3034, functioncode=4, signed=False) / 10 #Read AC Volts as Unsigned 16-Bit
    values['AC voltage 3 (V)'] = instrument.read_register(3035, functioncode=4, signed=False) / 10 #Read AC Volts as Unsigned 16-Bit

    values['AC Current 1 (A)'] = instrument.read_register(3036, functioncode=4, signed=False) / 10 #Read AC Frequency as Unsigned 16-Bit
    values['AC Current 2 (A)'] = instrument.read_register(3037, functioncode=4, signed=False) / 10 #Read AC Frequency as Unsigned 16-Bit
    values['AC Current 3 (A)'] = instrument.read_register(3038, functioncode=4, signed=False) / 10#Read AC Frequency as Unsigned 16-Bit

    values['AC Frequency (Hz)'] = instrument.read_register(3042, functioncode=4, signed=False) / 100 #Read AC Frequency as Unsigned 16-Bit
    values['Inverter Temperature (c)'] = instrument.read_register(3041, functioncode=4, signed=True) / 10 #Read Inverter Temperature as Signed 16-B$

    Realtime_DATA_yy = instrument.read_register(3072, functioncode=4, signed=False) #Read Year
    Realtime_DATA_mm = instrument.read_register(3073, functioncode=4, signed=False) #Read Month
    Realtime_DATA_dd = instrument.read_register(3074, functioncode=4, signed=False) #Read Day
    Realtime_DATA_hh = instrument.read_register(3075, functioncode=4, signed=False) #Read Hour
    Realtime_DATA_mi = instrument.read_register(3076, functioncode=4, signed=False) #Read Minute
    Realtime_DATA_ss = instrument.read_register(3077, functioncode=4, signed=False) #Read Second

    values['ac power (A)'] = instrument.read_register(3005, functioncode=4, signed=False) #Read AC Frequency as Unsigned 16-Bit
    values['pv power (V)'] = instrument.read_register(3007, functioncode=4, signed=False) #Read AC Frequency as Unsigned 16-Bit
    values['Total energy (W)'] = instrument.read_register(3009, functioncode=4, signed=False) #Read AC Frequency as Unsigned 16-Bit
    values['Month energy (W)'] = instrument.read_register(3011, functioncode=4, signed=False) #Read AC Frequency as Unsigned 16-Bit
    values['Last month energy (W)'] = instrument.read_register(3013, functioncode=4, signed=False) #Read AC Frequency as Unsigned 16-Bit
    values['Last year energy'] = instrument.read_register(3019, functioncode=4, signed=False) #Read AC Frequency as Unsigned 16-Bit

    if __debug__:
      print("Date : {:02d}-{:02d}-20{:02d} {:02d}:{:02d}:{:02d}".format(Realtime_DATA_dd, Realtime_DATA_mm, Realtime_DATA_yy, Realtime_DATA_hh, Realtime_DATA_mi, Realtime_DATA_ss) )
      print( json.dumps(values) )

    json_body = {'points': [{
                            'fields': {k: v for k, v in values.items()}
                                    }],
                        'measurement': influx_measurement
                        }

    client = InfluxDBClient(host=influx_server,
                            port=influx_port)
    success = client.write(json_body,
                        # params isneeded, otherwise error 'database is required' happens
                        params={'db': influx_database})

    if not success:
        print('error writing to database')

################## TEST TEST ###################################################
#found = [ 3004, 3005, 3007, 3008, 3009, 3011, 3013, 3014, 3019, 3021, 3022, 3023, 3024, 3033, 3034, 3035, 3036, 3037, 3038, 3042, 3041, 3072, 3073, 3074, 3075, 3076, 3077]

    values1 = dict()
    for i in range(2999, 3510, 1):
#    if not i in found:
        values1[i] = instrument.read_register(i, functioncode=4, signed=False) #Read AC Volts as Unsigned 16-Bit

    if __debug__:
      print("Date : {:02d}-{:02d}-20{:02d} {:02d}:{:02d}:{:02d}".format(Realtime_DATA_dd, Realtime_DATA_mm, Realtime_DATA_yy, Realtime_DATA_hh, Realtime_DATA_mi, Realtime_DATA_ss) )
      print( json.dumps(values1) )

    json_body = {'points': [{
                            'fields': {k: v for k, v in values1.items()}
                                    }],
                        'measurement': "test"
                        }

    client = InfluxDBClient(host=influx_server,
                            port=influx_port)
    success = client.write(json_body,
                        # params isneeded, otherwise error 'database is required' happens
                        params={'db': influx_database})

    if not success:
        print('error writing to database')


################## TEST TEST ###################################################

    client.close()

def openDatabase():
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
            print( dbclient.get_list_continuous_queries())

    except Exception as e:
        print('Error querying open database: ' )
        print(e)

openDatabase()
while True:
    getData()
    time.sleep( 30 )
