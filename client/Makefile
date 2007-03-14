PO_FILES=$(wildcard po/*/LC_MESSAGES/smolt.po)
MO_FILES=$(patsubst %.po,%.mo,$(PO_FILES))
PY_FILES=deleteProfile.py haldump.py __init__.py sendProfile.py smoltGui.py smolt.py software.py

all: po/smolt.pot $(MO_FILES)

po/smolt.pot: $(PY_FILES)
	pygettext.py -d smolt -o po/smolt.pot $^

%.po: po/smolt.pot
	msgmerge --update $@ $^

%.mo: %.po
	msgfmt.py -o $@ $<
