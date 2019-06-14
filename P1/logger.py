import time
import sys
import datetime
from influxdb import InfluxDBClient
import automationhat
#import RPi.GPIO as GPIO
 
# Set this variables, influxDB should be localhost on Pi
host = "localhost"
port = 8086
user = "root"
password = "root"
 
# The database we created
dbname = "logger"
# Sample period (s)
interval = 1
 
# For GPIO
# channel = 14¬
# GPIO.setmode(GPIO.BCM)¬
# GPIO.setup(channel, GPIO.IN)¬
 
# Allow user to set session and runno via args otherwise auto-generate
if len(sys.argv) > 1:
    if (len(sys.argv) < 3):
        print "Must define session and runNo!!"
        sys.exit()
    else:
        session = sys.argv[1]
        runNo = sys.argv[2]
else:
    session = "dev"
    now = datetime.datetime.now()
    runNo = now.strftime("%Y%m%d%H%M")
 
print "Session: ", session
print "runNo: ", runNo
 
# Create the InfluxDB object
client = InfluxDBClient(host, port, user, password, dbname)
 
# Run until keyboard out
try:
    while True:
        # This gets a dict of the three values
        vsense = automationhat.analog.read()
        op = automationhat.input.read()
        # gpio = GPIO.input(channel)
        print vsense
        print op
        iso = time.ctime()
 
        json_body = [
        {
          "measurement": session,
              "tags": {
                  "run": runNo,
                  },
              "time": iso,
              "fields": {
                  "op1" : op['one'], "op2" : op['two'], "op3" : op['three'],
                  "vsense1" : vsense['one'],"vsense2" : vsense['two'],"vsense3" : vsense['three']
                  # ,"gpio" : gpio
              }
          }
        ]
 
        # Write JSON to InfluxDB
        client.write_points(json_body)
        # Wait for next sample
        time.sleep(interval)
 
except KeyboardInterrupt:
    pass
    