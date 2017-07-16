#!/usr/bin/python

import socket
import time
import re
import os
import math
import datetime
import urllib2
from nordpool import elspot
from datetime import datetime, timedelta
import pytz

def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

# addressing information of target
IPADDR = '192.168.0.8'
PORTNUM = 8530

# enter the data content of the UDP packet as hex
PACKETDATAON = '0142accf232bc4ee104CF75F5A28A181574AC1B563CD51A78D'.decode('hex')
PACKETDATAOFF = '0142accf232bc4ee10F7B4E74B970D96F3CA2BB5D3CD1C19D0'.decode('hex')

DS18B20_ID_water = "28-031500c981ff"
DS18B20_TEMP_RE = re.compile(r't=(?P<temperature>[+-]?\d+)', re.M)

def get_temperature_from_sensor(sensor_name):
    """
    Parse output form the sensor
    """
    sensor_file = os.path.join(
        "/sys/bus/w1/devices/",
        sensor_name,
        "w1_slave")

    timestamp = int(time.time())
    with open(sensor_file, 'r') as f:
        data = f.read()

    found = DS18B20_TEMP_RE.search(data)
    if found is None:
        return (timestamp, None)
    return (timestamp, int(found.group('temperature')) / 1000.0)

timestamp, temperature =  get_temperature_from_sensor(DS18B20_ID_water)


#response = urllib2.urlopen('http://www.temperatur.nu/termo/uppsala/temp.txt')
#responsetext = response.read()
#if(responsetext == "N/A"):
#    outsideT = 10
#else:
#    outsideT = float(responsetext)

prices = elspot.Prices(currency='SEK')

now = datetime.now(pytz.utc) - timedelta(days=31)
q = prices.monthly(areas=['SE3'],end_date=now)
l = []
for i in q['areas']['SE3']['values']:
    l.append(i['value'])

average = mean(l[1:12])

now = datetime.now(pytz.utc)
prices = elspot.Prices(currency='SEK')
p = prices.hourly(areas=['SE3'],end_date=now)
for i in p['areas']['SE3']['values']:
    if((i['start'] <= now) & (i['end'] > now)):
        price = i['value']

pricediff = average - price

#now = datetime.datetime.now().minute/60.0 + datetime.datetime.now().hour

#targett = 1*math.sin((now+10)/(math.pi*1.2))+26+2/(1+math.exp(-0.25*(outsideT-10)))-1

targett = 26+2/(1+math.exp(-0.05*pricediff))
print(targett)
print(pricediff)
print(2/(1+math.exp(-0.05*pricediff)))

#now = datetime.datetime.now().minute/60.0 + datetime.datetime.now().hour

#targett = math.sin(((now-8)/(3.14159*1.2)))*1+24
#targett = 1.5*math.sin((now+10)/(math.pi*1.2))+25.5 


# initialize a socket, think of it as a cable
# SOCK_DGRAM specifies that this is UDP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)

# connect the socket, think of it as connecting the cable to the address location
s.connect((IPADDR, PORTNUM))

# send the command
if(targett > temperature+0.3):
    s.send(PACKETDATAON)

if(targett < temperature-0.3):
    s.send(PACKETDATAOFF)

# close the socket
s.close()

#print '{temp}'.format(temp=temperature)
#print '{temp}'.format(temp=targett)
