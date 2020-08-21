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
apikey = config.get('Weather', apikey)
country = config.get('Weather', country)
language = config.get('Weather', language)
# You MUST provide a valid API key

config_dict = get_default_config()
config_dict['language'] = language  # your language here

owm = pyowm.OWM(apikey, config_dict)

# Here put your city and Country ISO 3166 country codes
observation = owm.weather_at_place(country) 
w = observation.get_weather()
# Weather details from INTERNET 

w.status           # short version of status (eg. 'Rain')
w.detailed_status  # detailed version of status (eg. 'light rain')

wind = w.get_wind() 
speed = wind ["speed"] 
deg = wind ["deg"] 
humidity = w.get_humidity() 
temperature = w.get_temperature('celsius') 
temp = temperature["temp"] 
rain = w.get_rain() 

#If there is no data recorded from rain then return 0, otherwise #return the actual data
if len(rain) == 0: 
      lastrain = 0 
else: 
      lastrain = rain["3h"]

pressure = w.pressure['press']


# Print the data 
print "The status is: " + w.status
print "The status is: " + detailed_status
print "The velocity of the air is: " + str(speed) + " m/s" 
print "The wind direction is: " + str(deg) + " Degrees" 
print "The humidity is: " + str(humidity) + " %" 
print "The temperature is: " + str(temp) + " Celcius" 
print "The precipitation is: " + str(lastrain) + " mm"
print "The pressure is: " + str(pressure) + " mm"

