import locale
locale.setlocale(locale.LC_ALL, '')

import os

import gettext

if os.path.isdir('po'):
    # if there is a local directory called 'po' use it so we can test
    # without installing
    t = gettext.translation('smolt', 'po', fallback = True)
    
else:
    t = gettext.translation('smolt', fallback = True)

_ = t.gettext
