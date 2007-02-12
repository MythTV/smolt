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

'''systemMemory=1002&vendor=Dell+Inc.&UUID=391802cf-18ed-4f4c-b5c4-aa9a5fc2634c&language=en_US.UTF-8&CPUVendor=GenuineIntel&system=MXC051&bogomips=1597.33&platform=i686&CPUSpeed=799&systemSwap=2051&CPUModel=Intel%28R%29+Pentium%28R%29+M+processor+1.73GHz&OS=Fedora+Core+release+6+%28Zod%29&numCPUs=1&defaultRunlevel=5'''
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
'''VendorID=0x0&UUID=391802cf-18ed-4f4c-b5c4-aa9a5fc2634c&Bus=scsi_generic&Driver=Unknown&DeviceID=0x0&Class=None&Description=SCSI+Generic+Interface'''
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
 
