NAME=$(shell awk '/Name:/ { print $$2 }' hwdata.spec)
VERSION=$(shell awk '/Version:/ { print $$2 }' hwdata.spec)
RELEASE=$(shell awk '/Release:/ { a=$$2; sub("%.*","",a); print a }' hwdata.spec)
SOURCEDIR := $(shell pwd)

prefix=$(DESTDIR)/usr
sysconfdir=$(DESTDIR)/etc
bindir=$(prefix)/bin
sbindir=$(prefix)/sbin
datadir=$(prefix)/share
mandir=$(datadir)/man
includedir=$(prefix)/include
libdir=$(prefix)/lib

CC=gcc
CFLAGS=$(RPM_OPT_FLAGS) -g

CVSROOT = $(shell cat CVS/Root 2>/dev/null || :)

CVSTAG = $(NAME)-r$(subst .,-,$(VERSION))

FILES = MonitorsDB pci.ids upgradelist usb.ids videodrivers

.PHONY: all install tag force-tag check create-archive archive srpm-x clean clog new-pci-ids new-usb-ids

all: 

install:
	mkdir -p -m 755 $(datadir)/$(NAME)
	for foo in $(FILES) ; do \
		install -m 644 $$foo $(datadir)/$(NAME) ;\
	done
	mkdir -p -m 755 $(datadir)/$(NAME)/videoaliases
	mkdir -p -m 755 $(sysconfdir)/modprobe.d
	install -m 644 blacklist $(sysconfdir)/modprobe.d

tag:
	@cvs -Q tag $(CVSTAG)

force-tag:
	@cvs -Q tag -F $(CVSTAG)

check:
	[ -x /sbin/lspci ] && /sbin/lspci -i pci.ids > /dev/null
	./check-pci-ids.py
	@: videodrivers is tab-separated
	[ `grep -vc '	' videodrivers` -eq 0 ]

create-archive:
	@rm -rf /tmp/$(NAME)
	@cd /tmp ; cvs -Q -d $(CVSROOT) export -r$(CVSTAG) $(NAME) || echo "Um... export aborted."
	@mv /tmp/$(NAME) /tmp/$(NAME)-$(VERSION)
	@cd /tmp ; tar -czSpf $(NAME)-$(VERSION).tar.gz $(NAME)-$(VERSION)
	@rm -rf /tmp/$(NAME)-$(VERSION)
	@cp /tmp/$(NAME)-$(VERSION).tar.gz .
	@rm -f /tmp/$(NAME)-$(VERSION).tar.gz
	@echo ""
	@echo "The final archive is in $(NAME)-$(VERSION).tar.gz"

archive: check clean tag create-archive

dummy:

srpm-x: create-archive
	@echo Creating $(NAME) src.rpm
	@rpmbuild --nodeps -bs --define "_sourcedir $(SOURCEDIR)" --define "_srcrpmdir $(SOURCEDIR)" $(NAME).spec
	@echo SRPM is: $(NAME)-$(VERSION)-$(RELEASE).src.rpm

clean:
	@rm -f $(NAME)-*.gz $(NAME)-*.src.rpm

clog: hwdata.spec
	@sed -n '/^%changelog/,/^$$/{/^%/d;/^$$/d;s/%%/%/g;p}' $< | tee $@

new-usb-ids:
	@curl -O http://www.linux-usb.org/usb.ids

new-pci-ids:
	@curl -O http://pciids.sourceforge.net/pci.ids
