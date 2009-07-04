# Gentoo mirrorselect
# Written by Colin Kingsley (tercel@gentoo.org)
# Licensed under GPLv2
# Small refactorings by Sebastian Pipping <sebastian@pipping.org>

from HTMLParser import HTMLParser

class MirrorParser(HTMLParser):
    """
    MirrorParser objects are fed an html input stream via the feed() method.
    After the instance is closed, the lines atribute contains an array with
    elements of the form: (url, description)
    """

    def __init__(self):
        HTMLParser.__init__(self)

        self.lines = []
        self.line = []

        self.get_desc = False
        self.in_sect = False
        self.sect_good = False
        self.check_title = False

        self.sects = ('North America', 'South America', 'Europe', 'Australia',
                'Asia', 'Other Mirrors:', 'Partial Mirrors')

    def handle_starttag(self, tag, attrs):
        if tag == 'section':
            self.in_sect = True
        if (tag == 'title') and self.in_sect:
            self.check_title = True
        if (tag == 'uri') and self.sect_good:   #This is a good one
            self.line.append(dict(attrs)['link'])       #url
            self.get_desc = True        #the next data block is the description

    def handle_data(self, data):
        if self.check_title and (data in self.sects):
            self.sect_good = True
        if self.get_desc:
            if data.endswith('*'):
                data = data.replace('*', '')
                data = '* ' + data
            self.line.append(data)
            self.get_desc = False

    def handle_endtag(self, tag):
        if tag == 'section':
            self.in_sect = False
            self.sect_good = False
        if (tag == 'uri') and (len(self.line) == 2):
            self.lines.append(tuple(self.line))
            self.line = []
