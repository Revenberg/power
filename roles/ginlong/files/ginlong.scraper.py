#!/usr/bin/python
import requests
import urllib, urllib2
import json
import time

class ginlong(object):
    def __init__(self, username, password, domain, lan, deviceId, *args, **kwargs):
        try:
            # Create session for requests
            self.session = requests.session()

        # default heaeders gives a 403, seems releted to the request user agent, so we put curl here
        self.headers = {'User-Agent': 'curl/7.58.0'}
        self.self.cookies = {'language': lan}
    
        #login call
        self.params = {
            "userName": username,
            "password": password,
            "lan": lan,
            "domain": domain,
            "userType": "C"
        }
        url = 'https://'+domain+'/cpro/login/validateLogin.json'
        resultData = session.post(url, data=params, headers=headers)

        resultJson = resultData.json()
        if resultJson['result'].get('isAccept') == 1:
            print "Login Succesfull on",domain,"!"
        else:
            print "Login Failed on",domain,"!!"
            Exit()

        if self.deviceId == "deviceid":
            print ''
            print "Your deviceId is not set, auto detecting"
            url = 'http://'+domain+'/cpro/epc/plantview/view/doPlantList.json'

            
            resultData = session.get(url, cookies=self.cookies, headers=self.headers)
            resultJson = resultData.json()

            plantId = resultJson['result']['pagination']['data'][0]['plantId']

            url = 'http://'+domain+'/cpro/epc/plantDevice/inverterListAjax.json?'
            params = {
                'plantId': int(plantId)
            }
            
            resultData = session.get(url, params=params, cookies=self.cookies, headers=self.headers)
            resultJson = resultData.json()

            #.result.paginationAjax.data
            self.deviceId = resultJson['result']['paginationAjax']['data'][0]['deviceId']

        print "Your deviceId is ",self.deviceId

    def getData(self):
    #   get device details
        url = 'http://'+domain+'/cpro/device/inverter/goDetailAjax.json'
        params = {
            'deviceId': int(self.deviceId)
        }
    
        resultData = session.get(url, params=params, cookies=self.cookies, headers=self.headers)
        resultJson = resultData.json()
    
    #   Get values from json
        keys = {}
        keys['updateDate'] = resultJson['result']['deviceWapper'].get('updateDate')
        keys['DC_Voltage_PV1'] = resultJson['result']['deviceWapper']['dataJSON'].get('1a')
        keys['DC_Voltage_PV2'] = resultJson['result']['deviceWapper']['dataJSON'].get('1b')
        keys['DC_Current1'] = resultJson['result']['deviceWapper']['dataJSON'].get('1j')
        keys['DC_Current2'] = resultJson['result']['deviceWapper']['dataJSON'].get('1k')
        keys['AC_Voltage'] = resultJson['result']['deviceWapper']['dataJSON'].get('1ah')
        keys['AC_Current'] = resultJson['result']['deviceWapper']['dataJSON'].get('1ak')
        keys['AC_Power'] = resultJson['result']['deviceWapper']['dataJSON'].get('1ao')
        keys['AC_Frequency'] = resultJson['result']['deviceWapper']['dataJSON'].get('1ar')
        keys['DC_Power_PV1'] = resultJson['result']['deviceWapper']['dataJSON'].get('1s')
        keys['DC_Power_PV2'] = resultJson['result']['deviceWapper']['dataJSON'].get('1t')
        keys['Inverter_Temperature'] = resultJson['result']['deviceWapper']['dataJSON'].get('1df')
        keys['Daily_Generation'] = resultJson['result']['deviceWapper']['dataJSON'].get('1bd')
        keys['Monthly_Generation'] = resultJson['result']['deviceWapper']['dataJSON'].get('1be')
        keys['Annual_Generation'] = resultJson['result']['deviceWapper']['dataJSON'].get('1bf')
        keys['Total_Generation'] = resultJson['result']['deviceWapper']['dataJSON'].get('1bc')
        keys['Generation_Last_Month'] = resultJson['result']['deviceWapper']['dataJSON'].get('1ru')
        
        self._keys = keys

def check_db_status(options):
    # if the db is not found, then try to create it
    try:
        dbclient = InfluxDBClient(options.influx_hostname, options.influx_port, options.influx_username, options.influx_password)
        dblist = dbclient.get_list_database()
        db_found = False
        for db in dblist:
            if db['name'] == options.influx_database:
                db_found = True
        if not(db_found):
            logger.info('Database <%s> not found, trying to create it', options.influx_database)
            dbclient.create_database(options.influx_database)
            dbclient.create_retention_policy('30_days', '30d', 1, default=True)
            dbclient.create_retention_policy('6_months', '26wd', 1, default=False)
            dbclient.create_retention_policy('infinite', 'INF', 1, default=False)

        return True
    except Exception as e:
        logger.error('Error querying open-nti database: %s', e)
        return False

def send_to_influxdb(options, fields):

    req = {
        "measurement": options.influx_measurement,
        "tags": {},
        "time": int(time.ctime((updateDate) / 1000)),
        "fields": {}
    }

    if options.influx_tags is not None:
        for tag in options.influx_tags:
            tag_kv = tag.split('=')
            req['tags'][tag_kv[0]] = tag_kv[1]

    for field_k, field_v in fields.iteritems():
        if field_v is not None:
            req['fields'][field_k] = field_v

    reqs = []
    reqs.append(req)

    client = InfluxDBClient(options.influx_hostname, options.influx_port, options.influx_username, options.influx_password, options.influx_database)
    client.write_points(reqs, retention_policy=options.influx_retention_policy, database=options.influx_database)

def start_monitor(options):

    meter = ginlong(options.username, options.password, options.domain, options.lan, options.deviceId)

    try:

        while True:
            datagram = meter.read_one_packet()
            send_to_influxdb(options, datagram._keys)

    finally:
        meter.disconnect()

def main(argv=None):

    from argparse import ArgumentParser
   
    parser = ArgumentParser(description="Send ginlong request to an InfluxDB API")

    parser.add_argument("-u", "--username", dest="username", help="your portal username")
    parser.add_argument("-p", "--password", dest="password", help="your portal password", default='')
    parser.add_argument("-d", "--domain", dest="domain", help="domain ginlong used multiple domains with same login but different versions, could change anytime. monitoring.csisolar.com, m.ginlong.com", default='m.ginlong.com')
    parser.add_argument("-l", "--lan", dest="lan", help="lanuage (2 = English)", default='2')
    parser.add_argument("-i", "--deviceId", dest="deviceId", help="your deviceid, if set to deviceid it will try to auto detect, if you have more then one device then specify.", default='deviceid')
    
    influx_group = parser.add_argument_group()
    influx_group.add_argument("--influx-hostname", metavar='hostname', dest="influx_hostname", help="hostname to connect to InfluxDB, defaults to 'localhost'", default="localhost")
    influx_group.add_argument("--influx-port", metavar='port', dest="influx_port", help="port to connect to InfluxDB, defaults to 8086", type=int, default=8086)
    influx_group.add_argument("--influx-username", metavar='username', dest="influx_username", help="user to connect, defaults to 'root'", default="root")
    influx_group.add_argument("--influx-password", metavar='password', dest="influx_password", help="password of the user, defaults to 'root'", default="root")
    influx_group.add_argument("--influx-database", metavar='dbname', dest="influx_database", help="database name to connect to, defaults to 'ginlong'", default="ginlong")
    influx_group.add_argument("--influx-retention-policy", metavar='policy', dest="influx_retention_policy", help="retention policy to use")

    influx_group.add_argument("--influx-measurement", metavar='measurement', dest="influx_measurement", help="measurement name to store points, defaults to smartmeter", default="smartmeter")
    influx_group.add_argument('influx_tags', metavar='tag ...', type=str, nargs='?', help='any tag to the measurement')

    verbose_group = parser.add_mutually_exclusive_group()
    verbose_group.add_argument("-v", "--verbose", action="store_true", dest="verbose", help="Be verbose")
    verbose_group.add_argument("-q", "--quiet", action="store_true", dest="quiet", help="Be very quiet")

    args = parser.parse_args()

    check_db_status(args)
    start_monitor(args)

if __name__ == "__main__":
    import sys
    sys.exit(main())            