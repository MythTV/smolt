PO_FILES=$(wildcard po/*.po)
MO_FILES=$(patsubst %.po,%.mo,$(PO_FILES))
PY_FILES=deleteProfile.py haldump.py __init__.py sendProfile.py smoltGui.py smolt.py software.py smoltFirstBoot.py gui.py privacypolicy.py scan.py
DIRED_MO_FILES=$(patsubst po/%.mo,mo/%/LC_MESSAGES/$(NAME).mo,$(MO_FILES))
CLIENT_FILES=deleteProfile.py gui.py haldump.py i18n.py privacypolicy.py sendProfile.py smolt.py smoltGui.py software.py scan.py


NAME=smolt
ifndef DESTDIR
DESTDIR=/
else
DESTDIR:=$(abspath $(DESTDIR))
endif
ETC=$(DESTDIR)/etc
SMOLTCONFIGDIR=$(ETC)/smolt
PREFIX=$(DESTDIR)/usr
BINDIR=$(PREFIX)/bin
DATADIR=$(PREFIX)/share

all: po/smolt.pot $(MO_FILES)

po/smolt.pot: $(PY_FILES)
	xgettext -d smolt -o po/smolt.pot $^

%.po: po/smolt.pot
	msgmerge --no-wrap --update $@ $^

%.mo: %.po
	msgfmt -o $@ $<
	
.PHONY: install move-mo isnstall-main post-install monkey
install-main: move-mo
	mkdir -p $(ETC)/smolt/
	mkdir -p $(BINDIR)/
	mkdir -p $(DATADIR)/locale/
	
	cp -advr mo/* $(DATADIR)/locale/ 
	cp -advr config.py $(SMOLTCONFIGDIR)
	
	install -d -m 0755 ./ $(DATADIR)/$(NAME)/client/
	install -d -m 0755 icons/ $(DATADIR)/$(NAME)/client/icons/
	cp -adv $(CLIENT_FILES) $(DATADIR)/$(NAME)/client/
	
	
	mkdir -p $(DATADIR)/icons/hicolor/16x16/apps/
	mkdir -p $(DATADIR)/icons/hicolor/22x22/apps/
	mkdir -p $(DATADIR)/icons/hicolor/24x24/apps/
	mkdir -p $(DATADIR)/icons/hicolor/32x32/apps/
	
	cp ./icons/smolt-icon-16.png $(DATADIR)/icons/hicolor/16x16/apps/smolt.png
	cp ./icons/smolt-icon-22.png $(DATADIR)/icons/hicolor/22x22/apps/smolt.png
	cp ./icons/smolt-icon-24.png $(DATADIR)/icons/hicolor/24x24/apps/smolt.png
	cp ./icons/smolt-icon-32.png $(DATADIR)/icons/hicolor/32x32/apps/smolt.png
	
	mkdir -p $(DATADIR)/$(NAME)/doc
	install -p -m 0644 ../doc/PrivacyPolicy $(DATADIR)/$(NAME)/doc
	
	ln -sf $(DATADIR)/$(NAME)/client/sendProfile.py $(BINDIR)/smoltSendProfile
	ln -sf $(DATADIR)/$(NAME)/client/deleteProfile.py $(BINDIR)/smoltDeleteProfile
	ln -sf $(DATADIR)/$(NAME)/client/smoltGui.py $(BINDIR)/smoltGui
	
	chmod +x $(DATADIR)/$(NAME)/client/*Profile.py
	chmod +x $(DATADIR)/$(NAME)/client/smoltGui.py
	
	desktop-file-install --vendor='fedora' --dir=$(DATADIR)/applications ./smolt.desktop
	
move-mo: $(DIRED_MO_FILES)
	
$(DIRED_MO_FILES): mo/%/LC_MESSAGES/$(NAME).mo: po/%.mo
	mkdir -p mo/$*/LC_MESSAGES/
	cp $< $@

install: post-install

post-install: install-main

	mkdir -p $(ETC)/init.d/
	mkdir -p $(ETC)/cron.d/
	cp -adv smolt-init $(ETC)/init.d/smolt
	cp -adv smolt.cron.monthly $(ETC)/cron.d/smolt
	python makeuuid.py $(SMOLTCONFIGDIR)/hw-uuid
	
monkey: 
	echo $(abspath $(DESTDIR))	

	
