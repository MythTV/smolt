PO_FILES=$(wildcard po/*.po)
MO_FILES=$(patsubst %.po,%.mo,$(PO_FILES))
PY_FILES=deleteProfile.py haldump.py __init__.py sendProfile.py smoltGui.py smolt.py software.py smoltFirstBoot.py gui.py

all: po/smolt.pot $(MO_FILES)

po/smolt.pot: $(PY_FILES)
	pygettext.py -d smolt -o po/smolt.pot $^

%.po: po/smolt.pot
	msgmerge --no-wrap --update $@ $^

%.mo: %.po
	msgfmt.py -o $@ $<
