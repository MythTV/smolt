SMOON_URL = "http://smolt.fedoraproject.org/"

#Only a fool would edit what lays beyond here
#Are you that fool?


#For Redhat
try:
    OS = file('/etc/redhat-release').read().strip()
except IOError:
    OS = "Shadowman!"

HW_UUID = "/etc/sysconfig/hw-uuid"

##For SuSE
#try:
#    OS = file('/etc/SuSE-release').read().split('\n')[0].strip()
#except IOError:
#    OS = "It's a Lizard man!, It changes Colours!"
#
#    HW_UUID = "/etc/smolt/hw-uuid
#
##For Debian
#try:
#    #this is a bit of a kludge, as /etc/debian-release is 
#    #somewhat incomplete in what it gives you
#    #I also figure this should work better in 
#    #ubuntu
#    OS = file('/etc/issue.net').read().strip()
#except IOError:
#    OS = "The swirl, it's Spinning!"
#
#    HW_UUID = "/etc/smolt/hw-uuid
