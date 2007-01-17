
# all the crap that is stored on the rhn side of stuff
# updating/fetching package lists, channels, etc

import up2dateAuth
import up2dateErrors
import config
import rhnserver


from rhpl.translate import _



global channel_blacklist
channel_blacklist = []


# FIXME?
# change this so it doesnt import sourceConfig, but
# instead sourcesConfig imports rhnChannel (and repoDirector)
# this use a repoDirector.repos.parseConfig() or the like for
# each line in "sources", which would then add approriate channels
# to rhnChannel.selected_channels and populate the sources lists
# the parseApt/parseYum stuff would move to repoBackends/*Repo.parseConfig()
# instead... then we should beable to fully modularize the backend support


# heh, dont get much more generic than this...
class rhnChannel:
    # shrug, use attributes for thetime being
    def __init__(self, **kwargs):
        self.dict = {}

        for kw in kwargs.keys():
            self.dict[kw] = kwargs[kw]
               
    def __getitem__(self, item):
        return self.dict[item]

    def __setitem__(self, item, value):
        self.dict[item] = value

    def keys(self):
        return self.dict.keys()

    def values(self):
        return self.dict.values()

    def items(self):
        return self.dict.items()

class rhnChannelList:
    def __init__(self):
        # probabaly need to keep these in order for
        #precedence
        self.list = []

    def addChannel(self, channel):
        self.list.append(channel)


    def channels(self):
        return self.list

    def getByLabel(self, channelname):
        for channel in self.list:
            if channel['label'] == channelname:
                return channel
    def getByName(self, channelname):
        return self.getByLabel(channelname)

    def getByType(self, type):
        channels = []
        for channel in self.list:
            if channel['type'] == type:
                channels.append(channel)
        return channels

# for the gui client that needs to show more info
# maybe we should always make this call? If nothing
# else, wrapper should have a way to show extended channel info
def getChannelDetails():

    channels = []
    sourceChannels = getChannels()

    s = rhnserver.RhnServer()
    up2dateChannels = s.up2date.listChannels(up2dateAuth.getSystemId())

    for sourceChannel in sourceChannels.channels():
        if sourceChannel['type'] != 'up2date':
            # FIMXE: kluge since we dont have a good name, maybe be able to fix
            sourceChannel['name'] = sourceChannel['label']
            sourceChannel['description'] = "%s channel %s from  %s" % (sourceChannel['type'],
                                                                           sourceChannel['label'],
                                                                           sourceChannel['url'])
            channels.append(sourceChannel)
            continue
    
        for up2dateChannel in up2dateChannels:
            if up2dateChannel['label'] != sourceChannel['label']:
                continue
            for key in up2dateChannel.keys():
                sourceChannel[key] = up2dateChannel[key]
            channels.append(sourceChannel)
            

    return channels

cmdline_pkgs = []

global selected_channels
selected_channels = None
def getChannels(force=None, label_whitelist=None):
    cfg = config.initUp2dateConfig()
    global selected_channels
    if not selected_channels and not force:

        selected_channels = rhnChannelList()
        
        li = up2dateAuth.getLoginInfo()
        # login can fail...
        if li:    
            tmp = li.get('X-RHN-Auth-Channels')
            if tmp == None:
                tmp = []
            for i in tmp:
                if label_whitelist and not label_whitelist.has_key(i[0]):
                    continue
                
                channel = rhnChannel(label = i[0], version = i[1],
                                     type = 'up2date', url = cfg["serverURL"])
                selected_channels.addChannel(channel)

            if len(selected_channels.list) == 0:
                raise up2dateErrors.NoChannelsError(_("This system may not be updated until it is associated with a channel."))

    return selected_channels
            

def setChannels(tempchannels):
    global selected_channels
    selected_channels = None
    whitelist = dict(map(lambda x: (x,1), tempchannels))
    return getChannels(label_whitelist=whitelist)



def subscribeChannels(channels,username,passwd):
    s = rhnserver.RhnServer()
    s.up2date.subscribeChannels(up2dateAuth.getSystemId(), channels, username,
        passwd)

def unsubscribeChannels(channels,username,passwd):
    s = rhnserver.RhnServer()
    s.up2date.unsubscribeChannels(up2dateAuth.getSystemId(), channels,
        username, passwd)
