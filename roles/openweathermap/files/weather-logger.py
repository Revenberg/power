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

        wind  = w.get_wind()
        values['wind_speed']  = wind ["speed"]
        values['wind_direction_deg']  = wind ["deg"]
        values['humidity']  = w.get_humidity()
        temperature  = w.get_temperature('celsius')
        values['temp']  = temperature["temp"]
        values['pressure'] = w.get_pressure()['press']
        values['clouds'] = w.get_clouds() #Cloud coverage
        values["sunrise"] = w.get_sunrise_time() #Sunrise time (GMT UNIXtime or ISO 8601)
        values["sunset"] = w.get_sunset_time() #Sunset time (GMT UNIXtime or ISO 8601)
        values["weather_code"] =  w.get_weather_code()
        values["weather_icon"] = w.get_weather_icon_name()
        location = observation.get_location().get_name()
        values["location"] = location

        rain = w.get_rain()
        #If there is no data recorded from rain then return 0, otherwise #return the actual data
        if len(rain) == 0:
            values['lastrain'] = 0.0
        else:
            if "3h" in rain:
               values['lastrain'] = rain["3h"]
            if "1h" in rain:
               values['lastrain'] = rain["1h"]
            
        snow = w.get_snow()
        #If there is no data recorded from rain then return 0, otherwise #return the actual data
        if len(snow) == 0:
            values['lastsnow'] = 0.0
        else:
            if "3h" in snow:
               values['lastsnow'] = snow["3h"]
            if "1h" in snow:
               values['lastsnow'] = snow["1h"]            
        
        # Print the data
        if __debug__:
            print(values)

        json_body = {'points': [{
                                 'tags': {'location':  location },
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

        client.close()

        time.sleep( 300 )
except Exception as e:
    print(e)
    print("Unexpected error:", sys.exc_info()[0])
#        raise
finally:
    if __debug__:
        print("Finally")