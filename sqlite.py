#!/usr/bin/python
#!/usr/bin/env python
from __future__ import division
import os
import sys
import time
import re
import sqlite3
from subprocess import check_output,call
import spidev

isw = int(sys.argv[1])

#print isw

if((isw != -1) and (isw != 0) and (isw != 1) and (isw != 2) and (isw != 10) and (isw != 11) and (isw != 12)):
   sys.exit("Aaaa!!!")

gpio="/usr/local/bin/gpio"

DS18B20_ID = "28-031500c850ff"
DS18B20_ID_soil = "28-031500c981ff"
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
    return (timestamp, int(found.group('temperature')) / 1000)


# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def ReadChannel(channel,trans):
  spi = spidev.SpiDev()
  spi.open(0,0)
  check_output([gpio, "mode", trans,"out"])
  check_output([gpio, "write", trans,"1"])
  time.sleep(1)
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  adc2 = spi.xfer2([1,(8+channel)<<4,0])
  data2 = ((adc2[1]&3) << 8) + adc2[2]
  check_output([gpio, "write", trans,"0"])
  return (data+data2)/2.0

def ReadRadiation(channel):
  return float(check_output([gpio, "aread", channel]))

def collectData(c,isw):
  timestamp, temperature =  get_temperature_from_sensor(DS18B20_ID)
  timestamp, temperature_soil =  get_temperature_from_sensor(DS18B20_ID_soil)
  c.execute("SELECT julianday('now')-julianday(date) FROM messwerte WHERE (water == 1 OR water == 2) ORDER BY date desc limit 1")
  lastw = c.fetchone()[0]
  return (temperature,temperature_soil,ReadChannel(0,"4"),ReadRadiation("0"),lastw,isw)

#################################################################################

conn = sqlite3.connect('/home/odroid/tinkering/historic.db')

c = conn.cursor()

# Create table
#c.execute('''CREATE TABLE messwerte (date text, atemp real, stemp real, moist real, rad real, lwater real, water num);''')

data = collectData(c,isw)

print data

# Insert a row of data
c.execute("INSERT INTO messwerte VALUES (datetime('now'),?,?,?,?,?,?)",data)

# Save (commit) the changes
conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()
