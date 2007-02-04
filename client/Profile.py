#!/usr/bin/python

import hardware
import software
import sys
import os
import re

# use hardware to get what we need as different archs get data from different
# functions.  namely dmi is a bios only thing while  ppc and sparc have the
# information elsewhere.  
# EFI is currently of unknown status

class Profile:
    def __init__(self):
        try:
            self.UUID = file('/etc/sysconfig/hw-uuid').read().strip()
        except IOError:
            try:
                self.UUID = file('/proc/sys/kernel/random/uuid').read().strip()
                try:
                    file('/etc/sysconfig/hw-uuid', 'w').write(self.UUID)
                except:
                    sys.stderr.write('Unable to save UUID, continuing...\n')
            except IOError:
                sys.stderr.write('Unable to determine UUID of system!\n')
                sys.exit(1)

        self.hw = hardware.Hardware()
        
        self.lsbRelease = software.read_lsb_release().strip()
        
        self.OS = software.read_os().strip()
        
        self.defaultRunlevel = software.read_runlevel().strip()
        
	try:
        	self.language = os.environ['LANG']
	except KeyError:
		self.language = 'Unknown'

        self.platform = self.bogomips = self.CPUVendor = self.numCPUs = self.CPUSpeed = self.systemMemory = self.systemSwap = self.vendor = self.system = ''

        for device in self.hw:
            try:
                self.platform = device['platform'].strip()
                self.bogomips = device['bogomips'].strip()
                self.CPUVendor = "%s - %s" % (device['type'], device['model']).strip()
                self.numCPUs = device['count'].strip()
                self.CPUSpeed = device['speed'].strip()
            except:
                pass
            try:
                self.systemMemory = device['ram']
                self.systemSwap = device['swap'].strip()
            except:
                pass
            try:
                self.vendor = device['vendor'].strip()
                self.system = device['system'].strip()
            except:
                pass

        # Defaults for when hardware doesnt return anything.  namely a new cpu type 
        if self.platform == '':
            self.platform = 'Unknown'
        if self.bogomips == '':
            self.bogomips = 0
        if self.CPUVendor == '':
            self.CPUVendor = 'Unknown'
        if self.numCPUs == '':
            self.numCPUs = 1
        if self.CPUSpeed == '':
            self.CPUSpeed = 0
        if self.systemMemory == '':
            self.systemMemory = 0
        if self.systemSwap == '':
            self.systemSwap = 0
        if self.vendor == '':
            self.vendor = 'Unknown'
        if self.system == '':
            self.system = 'Unknown'

        # If the CPU can do frequency scaling the CPU speed returned
        # by /proc/cpuinfo might be less than the maximum possible for
        # the processor. Check sysfs for the proper file, and if it
        # exists, use that value.  Only use the value from CPU #0 and
        # assume that the rest of the CPUs are the same.
        
        if os.path.exists('/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq'):
            self.CPUSpeed = int(file('/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq').read().strip()) / 1000
            
    def get_host_string(self):
        return "UUID=%s&lsbRelease=%s&OS=%s&defaultRunlevel=%s&language=%s&platform=%s&bogomips=%s&CPUVendor=%s&numCPUs=%s&CPUSpeed=%s&systemMemory=%s&systemSwap=%s&vendor=%s&system=%s" % (self.UUID, self.lsbRelease, self.OS, self.defaultRunlevel, self.language, self.platform, self.bogomips, self.CPUVendor, self.numCPUs, self.CPUSpeed, self.systemMemory, self.systemSwap, self.vendor, self.system)

    def get_device_string(self):
        for device in self.hw:
            try:
                Bus = device['bus']
                Driver = device['driver']
                Class = device['class']
                Description = device['desc']
            except:
                continue
            else:
                yield "UUID=%s&Bus=%s&Driver=%s&Class=%s&Description=%s" % (self.UUID, Bus, Driver, Class, Description)

    def print_data(self):
        print '\tUUID: %s' % self.UUID
        print '\tlsbRelease: %s' % self.lsbRelease
        print '\tOS: %s' % self.OS
        print '\tdefaultRunlevel: %s' % self.defaultRunlevel
        print '\tlanguage: %s' % self.language
        print '\tplatform: %s' % self.platform
        print '\tbogomips: %s' % self.bogomips
        print '\tCPUVendor: %s' % self.CPUVendor
        print '\tnumCPUs: %s' % self.numCPUs
        print '\tCPUSpeed: %s' % self.CPUSpeed
        print '\tsystemMemory: %s' % self.systemMemory
        print '\tsystemSwap: %s' % self.systemSwap
        print '\tvendor: %s' % self.vendor
        print '\tsystem: %s' % self.system
        print
        print '\t\t Devices'
        print '\t\t================================='
        for device in self.hw:
            try:
                Bus = device['bus']
                Driver = device['driver']
                Class = device['class']
                Description = device['desc']
            except:
                continue
            else:
                print '\t\t%s, %s, %s, %s' % (Bus, Driver, Class, Description)
        
