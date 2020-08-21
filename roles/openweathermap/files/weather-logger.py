import pyowm
import os
import socket
import binascii
import time
import sys
import configparser
from influxdb import InfluxDBClient

config = configparser.RawConfigParser(allow_no_value=True)
config.read("config.ini")

log_path = config.get('Logging', 'log_path', fallback='/var/log/solar/')
do_raw_log = config.getboolean('Logging', 'do_raw_log')
apikey = config.get('Weather', 'apikey')
country = config.get('Weather', 'country')
language = config.get('Weather', 'language')

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
        print('Database ' + influx_database + ' not found, trying to create it')
        dbclient.create_database(influx_database)
        dbclient.create_retention_policy('30_days', '30d', 1, default=True)
        dbclient.create_retention_policy('6_months', '26wd', 1, default=False)
        dbclient.create_retention_policy('infinite', 'INF', 1, default=False)

except Exception as e:
    print('Error querying open database: ' + e)

try:
    while True:
        owm = pyowm.OWM(apikey, language=language)
        # Here put your city and Country ISO 3166 country codes
        observation = owm.weather_at_place(country)

        w = observation.get_weather()
        # Weather details from INTERNET

        values = dict()
        values['status'] = w.get_status()         # short version of status (eg. 'Rain')
        values['detailed_status']  = w.get_detailed_status()  # detailed version of status (eg. 'light rain')

        values['wind']  = w.get_wind()
        values['speed']  = wind ["speed"]
        values['deg']  = wind ["deg"]
        values['humidity']  = w.get_humidity()
        values['temperature']  = w.get_temperature('celsius')
        values['temp']  = temperature["temp"]
        values['pressure'] = w.get_pressure()['press']

        rain = w.get_rain()
        #If there is no data recorded from rain then return 0, otherwise #return the actual data
        if len(rain) == 0:
            values['lastrain'] = 0
        else:
            values['lastrain'] = rain["3h"]

        # Print the data
        print(values)

        json_body = {'points': [{'tags': 'fields': {k: v for k, v in values.items()}
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

                client.close()

        time.sleep( 300 )
    except Exception as e:
        print(e)
        print("Unexpected error:", sys.exc_info()[0])
#        raise
    finally:
        if __debug__:
            print("Finally")