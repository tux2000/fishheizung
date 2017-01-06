#!/usr/bin/python

import socket
import time
import re
import os
import math
import datetime
import urllib2

response = urllib2.urlopen('http://www.temperatur.nu/termo/uppsala/temp.txt')
outsideT = float(response.read())
print outsideT

now = datetime.datetime.now().minute/60.0 + datetime.datetime.now().hour

targett = 0.5*math.sin((now+10)/(math.pi*1.2))+25.5+2/(1+math.exp(-0.25*(outsideT-10)))-1

print targett
