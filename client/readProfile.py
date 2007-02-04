#!/usr/bin/python

import sys
sys.path.append('/usr/share/smolt/client')

import Profile
# Read the profile
profile = Profile.Profile()

#Print the profile
print 'We would send the following information to the Fedora Smolt server:'
print
profile.print_data()
