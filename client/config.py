
import os,re
import commands
import os_detect

SMOON_URL = "http://www.smolts.org/"
SECURE = 0


#Only a fool would edit what lays beyond here
#Are you that fool?

HW_UUID = "/etc/smolt/hw-uuid"
PUB_UUID = "/etc/smolt/pub-uuid"
#UUID_DB = "/etc/smolt/uuiddb.cfg"
#ADMIN_TOKEN = "/etc/sysconfig/smolt-token"


#These are the defaults taken from the source code.
#fs_types = get_config_attr("FS_TYPES", ["ext2", "ext3", "xfs", "reiserfs"])
#fs_mounts = get_config_attr("FS_MOUNTS", ["/", "/home", "/etc", "/var", "/boot"])
#fs_m_filter = get_config_attr("FS_M_FILTER", False)
#fs_t_filter = get_config_attr("FS_T_FILTER", False)

FS_T_FILTER=False
FS_M_FILTER=True
FS_MOUNTS=commands.getoutput('rpm -ql filesystem').split('\n') + ['/']


#This will attempt to find the distro.
OS = os_detect.get_os_info()

#Uncomment and customise for your distro if os_detect fails
#example
#try:
#    OS = file('/etc/distro-release').read().strip()
#except IOError:
#    OS = "Unknown"


