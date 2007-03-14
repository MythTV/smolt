#

po/smolt.pot: deleteProfile.py haldump.py __init__.py sendProfile.py smoltGui.py smolt.py software.py
	pygettext.py -d smolt -o po/smolt.pot $^

po/%.mo: po/%.po
	msgfmt.py -o $@ $<
