import pyowm
import os
import socket
import binascii
import time
import sys
import configparser
from influxdb import InfluxDBClient

config = configparser.RawConfigParser(allow_no_value=True)
config.read("weather_config.ini")

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
        print( dbclient.get_list_continuous_queries())

#select_clause = 'SELECT mean("value") INTO "cpu_mean" ' \
#                'FROM "weather" GROUP BY time(1m)'
#client.create_continuous_query(
#     'cpu_mean', select_clause, 'influx_database', 'EVERY 10s FOR 2m'

#CREATE CONTINUOUS QUERY "cq_30m" ON "food_data" BEGIN
# SELECT mean("website") AS "mean_website",mean("phone") AS "mean_phone"
#  INTO "a_year"."downsampled_orders"
#  FROM "orders"
#  GROUP BY time(30m)
#END

except Exception as e:
    print('Error querying open database: ' )
    print(e)

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
        values["visibility_distance"] = w.get_visibility_distance()      

        location = observation.get_location().get_name()
        values["location"] = location

        rain = w.get_rain()
        #If there is no data recorded from rain then return 0, otherwise #return the actual data
        if len(rain) == 0:
            values['lastrain'] = float("0")
        else:
            if "3h" in rain:
               values['lastrain'] = rain["3h"]
            if "1h" in rain:
               values['lastrain'] = rain["1h"]
            
        snow = w.get_snow()
        #If there is no data recorded from rain then return 0, otherwise #return the actual data
        if len(snow) == 0:
            values['lastsnow'] = float("0")
        else:
            if "3h" in snow:
               values['lastsnow'] = snow["3h"]
            if "1h" in snow:
               values['lastsnow'] = snow["1h"]            

#       UV index
        s = country.split(",")
        reg = owm.city_id_registry()
        list_of_locations = reg.locations_for(s[0], country=s[1])
        myLocation = list_of_locations[0]
        
        values['uvi'] = owm.uvindex_around_coords(myLocation.get_lat(), myLocation.get_lon()).get_value()  

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

        json_body = {'points': [{
                                 'fields': {'weather':  '1' }
                                        }],
                            'measurement': 'keepalive'
                            }

        success = client.write(json_body,
                            # params isneeded, otherwise error 'database is required' happens
                            params={'db': influx_database})

        if not success:
            print('error writing to database')

        client.close()

        time.sleep( 360 )
except Exception as e:
    print(e)
    print("Unexpected error:", sys.exc_info()[0])
#        raise
finally:
    if __debug__:
        print("Finally")