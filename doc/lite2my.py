#!/usr/bin/python

import sqlite
import sys
from urllib import urlencode

debug = True
smoonURL = "http://localhost:8080"

conn = sqlite.connect("/home/mmcgrath/hg/smolt/devdata.sqlite")
cursor = conn.cursor()

def selectQuery(query):
    """ Run query and return the results """
    try:
        cursor.execute(query)
    except sqlite.Error, err:
        if debug == True:
            print "%s" % err
            print "Query: %s" % query
            sys.exit(1)
    return cursor

hosts = selectQuery('select * from host;')
for host in hosts:
    UUID = host[1]
    LSB = host[2]
    OS = host[3]
    platform = host[4]
    bogomips = host[5]
    systemMemory = host[6]
    systemSwap = host[7]
    vendor = host[8]
    model = host[9]
    CPU = host[10]
    numCpus = host[11]
    cpuSpeed = host[12]
    language = host[13]
    defaultRunlevel = host[14]

    postData = urlencode({
                            'UUID' :        UUID,
                            'OS' :  OS,
                            'platform' : platform,
                            'bogomips' : bogomips,
                            'systemMemory' : systemMemory,
                            'systemSwap' : systemSwap,
                            'vendor' : vendor,
                            'system' : model,
                            'CPUVendor' : CPU.split(' - ')[0].strip(),
                            'CPUModel' : CPU.split(' - ')[1].strip(),
                            'numCPUs' : numCpus,
                            'CPUSpeed' : cpuSpeed,
                            'language' : language,
                            'defaultRunlevel' : defaultRunlevel })
#    print 'wget -qO- %s/add --post-data "%s"' % (smoonURL, postData)


devices = selectQuery('select host_links.host_u_u_id as UUID, device.description, device.bus, device.class, device.driver from host_links, device where host_links.device_id=device.id;')
for device in devices:
    UUID = device[0]
    try:
        description = device[1].split('|')[1]
    except:
        description = device[1]
    bus = device[2]
    type = device[3]
    driver = device[4]
    postData = urlencode({
                'UUID' : UUID,
                'Description' : description,
                'Bus' : bus,
                'Class' : type,
                'Driver' : driver,
                'VendorID' : '0x0',
                'DeviceID' : '0x0'
                })
    print 'wget -qO- %s/addDevice --post-data "%s"' % (smoonURL, postData)
 
