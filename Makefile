NAME=$(shell awk '/Name:/ { print $$2 }' hwdata.spec)
VERSION=$(shell awk '/Version:/ { print $$2 }' hwdata.spec)
RELEASE=$(shell rpm -q --define 'dist .el6' --specfile --qf "%{release}" hwdata.spec)
ifeq ($(shell git rev-parse --abbrev-ref HEAD | sed -n 's/^\([^0-9-]\+\).*/\L\1/p'), rhel)
    # add revision to tag name for rhel branches
    TAGNAME := $(NAME)-$(VERSION)-$(RELEASE)
else
    TAGNAME := $(NAME)-$(VERSION)
endif
SOURCEDIR := $(shell pwd)
ARCHIVE := $(TAGNAME).tar.bz2

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

IDFILES := pci.ids usb.ids oui.txt pnp.ids

FILES = MonitorsDB upgradelist videodrivers $(IDFILES)

.PHONY: all install tag force-tag check commit create-archive archive srpm-x clean clog new-pci-ids new-usb-ids

all: 

install:
	mkdir -p -m 755 $(datadir)/$(NAME)
	for foo in $(FILES) ; do \
		install -m 644 $$foo $(datadir)/$(NAME) ;\
	done
	mkdir -p -m 755 $(datadir)/$(NAME)/videoaliases
	mkdir -p -m 755 $(sysconfdir)/modprobe.d
	install -m 644 blacklist.conf $(sysconfdir)/modprobe.d

commit:
	git commit -vas ||:

tag:
	@git tag -s -m "Tag as $(TAGNAME)" $(TAGNAME)
	@echo "Tagged as $(TAGNAME)"

force-tag:
	@git tag -s -m "Tag as $(TAGNAME)" -f $(TAGNAME)
	@echo "Tag forced as $(TAGNAME)"

changelog:
	@rm -f ChangeLog
	@(GIT_DIR=.git git log > .changelog.tmp && mv .changelog.tmp ChangeLog || rm -f .changelog.tmp) || (touch ChangeLog; echo 'git directory not found: installing possibly empty changelog.' >&2)

check:
	@[ -x /sbin/lspci ] && /sbin/lspci -i pci.ids > /dev/null || { echo "FAILURE: /sbin/lspci -i pci.ids"; exit 1; } && echo "OK: /sbin/lspci -i pci.ids"
	@./check-pci-ids.py || { echo "FAILURE: ./check-pci-ids.py"; exit 1; } && echo "OK: ./check-pci-ids.py"
	@./check-usb-ids.sh
	@for file in $(IDFILES); do \
	    text=`LANG=C file $$file`; \
	    expected="$$file: UTF-8 Unicode text"; \
	    if [[ "$$text" != "$$expected" ]]; then \
		printf "Expected: %s\n Got instead: %s\n" "$$expected" "$$text" >&2; \
		exit 1; \
	    fi; \
	    echo "OK: $$text"; \
	done
	@echo -n "CHECK date of pci.ids: "; grep "Date:" pci.ids | cut -d ' ' -f 5
	@echo -n "CHECK date of usb.ids: "; grep "Date:" usb.ids | cut -d ' ' -f 6
	@: videodrivers is tab-separated
	@[ `grep -vc '	' videodrivers` -eq 0 ] || { echo "FAILURE: videodrivers not TAB separated"; exit 1; } && echo "OK: videodrivers"

create-archive:
	@rm -rf $(TAGNAME) $(TAGNAME).tar*  2>/dev/null
	@make changelog
	@git archive --format=tar --prefix=$(TAGNAME)/ HEAD > $(TAGNAME).tar
	@mkdir $(TAGNAME)
	@cp ChangeLog $(TAGNAME)/
	@tar --append -f $(TAGNAME).tar $(TAGNAME)
	@bzip2 -f $(TAGNAME).tar
	@rm -rf $(TAGNAME)
	@echo ""
	@echo "The final archive is in $(ARCHIVE)"

archive: check clean commit tag create-archive

upload:
	@scp $(ARCHIVE) fedorahosted.org:$(NAME)

dummy:

srpm-x: create-archive
	@echo Creating $(NAME) src.rpm
	@rpmbuild --nodeps -bs --define "_sourcedir $(SOURCEDIR)" --define "_srcrpmdir $(SOURCEDIR)" $(NAME).spec
	@echo SRPM is: $(NAME)-$(VERSION)-$(RELEASE).src.rpm

clean:
	@rm -f $(NAME)-*.bz2 $(NAME)-*.src.rpm

clog: hwdata.spec
	@sed -n '/^%changelog/,/^$$/{/^%/d;/^$$/d;s/%%/%/g;p}' $< | tee $@

download: new-usb-ids new-pci-ids new-oui

new-usb-ids:
	@curl -O http://www.linux-usb.org/usb.ids

new-pci-ids:
	@curl -O https://raw.githubusercontent.com/pciutils/pciids/master/pci.ids

new-oui:
	@curl -O http://standards-oui.ieee.org/oui.txt
	@dos2unix oui.txt
