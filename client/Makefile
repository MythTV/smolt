PO_FILES=$(wildcard po/*.po)
MO_FILES=$(patsubst %.po,%.mo,$(PO_FILES))
# echo PY_FILES=$(ls -1 *.py | grep -v '^\(create_monthly\|getLink\|haldump\|hammer_add\|makeuuid\|starhscale\).py$' | sort)
PY_FILES=config.py deleteProfile.py fs_util.py gate.py gui.py i18n.py __init__.py os_detect.py privacypolicy.py scan.py sendProfile.py smolt_config.py smoltFirstBoot.py smoltGui.py smolt.py software.py uuiddb.py
DIRED_MO_FILES=$(patsubst po/%.mo,mo/%/LC_MESSAGES/$(NAME).mo,$(MO_FILES))


NAME=smolt
ETC=$(DESTDIR)/etc
SMOLTCONFIGDIR=$(ETC)/smolt
PREFIX=$(DESTDIR)/usr
BINDIR=$(PREFIX)/bin
DATADIR=$(PREFIX)/share

ifndef DOCDIR
_DOCDIR=$(DATADIR)/$(NAME)/doc
else
_DOCDIR=$(DESTDIR)/$(DOCDIR)
endif

ifndef MANDIR
_MANDIR=$(DATADIR)/man
else
_MANDIR=$(DESTDIR)/$(MANDIR)
endif

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
	mkdir -p $(_MANDIR)/man1
	
	cp -advr mo/* $(DATADIR)/locale/ 
	cp -advr config.py $(SMOLTCONFIGDIR)
	
	install -d -m 0755 ./ $(DATADIR)/$(NAME)/client/
	install -D -m 0644 icons/exit.png $(DATADIR)/$(NAME)/client/icons/exit.png
	install -D -m 0644 icons/home.png $(DATADIR)/$(NAME)/client/icons/home.png
	install -D -m 0644 icons/privacy.png $(DATADIR)/$(NAME)/client/icons/privacy.png
	install -D -m 0644 icons/send-profile.png $(DATADIR)/$(NAME)/client/icons/send-profile.png
	install -D -m 0644 icons/smolt.png $(DATADIR)/$(NAME)/client/icons/smolt.png
	cp -adv $(PY_FILES) $(DATADIR)/$(NAME)/client/
	
	mkdir -p $(DATADIR)/icons/hicolor/16x16/apps/
	mkdir -p $(DATADIR)/icons/hicolor/22x22/apps/
	mkdir -p $(DATADIR)/icons/hicolor/24x24/apps/
	mkdir -p $(DATADIR)/icons/hicolor/32x32/apps/
	
	cp ./icons/smolt-icon-16.png $(DATADIR)/icons/hicolor/16x16/apps/smolt.png
	cp ./icons/smolt-icon-22.png $(DATADIR)/icons/hicolor/22x22/apps/smolt.png
	cp ./icons/smolt-icon-24.png $(DATADIR)/icons/hicolor/24x24/apps/smolt.png
	cp ./icons/smolt-icon-32.png $(DATADIR)/icons/hicolor/32x32/apps/smolt.png
	
	mkdir -p $(_DOCDIR)
	install -p -m 0644 ../doc/PrivacyPolicy $(_DOCDIR)
	
	gzip -c -9 man/smoltSendProfile.1 > $(_MANDIR)/man1/smoltSendProfile.1.gz
	gzip -c -9 man/smoltDeleteProfile.1 > $(_MANDIR)/man1/smoltDeleteProfile.1.gz
	gzip -c -9 man/smoltGui.1 > $(_MANDIR)/man1/smoltGui.1.gz
	
	ln -sf $(DATADIR)/$(NAME)/client/sendProfile.py $(BINDIR)/smoltSendProfile
	ln -sf $(DATADIR)/$(NAME)/client/deleteProfile.py $(BINDIR)/smoltDeleteProfile
	ln -sf $(DATADIR)/$(NAME)/client/smoltGui.py $(BINDIR)/smoltGui
	ln -sf $(SMOLTCONFIGDIR)/config.py $(DATADIR)/$(NAME)/client/config.py
	
	chmod +x $(DATADIR)/$(NAME)/client/*Profile.py
	chmod +x $(DATADIR)/$(NAME)/client/smoltGui.py
	
	mkdir -p $(DATADIR)/applications
	cp smolt.desktop $(DATADIR)/applications/

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
	
uuid:
	python makeuuid.py $(SMOLTCONFIGDIR)/hw-uuid True
	
cron:
	python create_monthly.py > smolt.cron.monthly
	cp -adv smolt.cron.monthly $(ETC)/cron.d/smolt
	
monkey: 
	echo $(abspath $(DESTDIR))	
