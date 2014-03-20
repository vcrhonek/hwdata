NAME=hwdata
VERSION=$(shell awk '/Version:/ { print $$2 }' hwdata.spec)
RELEASE=$(shell rpm -q --define 'dist %{nil}' --specfile --qf "%{release}" hwdata.spec)
ifeq ($(shell git rev-parse --abbrev-ref HEAD | sed -n 's/^\([^0-9-]\+\).*/\L\1/p'), rhel)
    # add revision to tag name for rhel branches
    TAGNAME := $(NAME)-$(VERSION)-$(RELEASE)
else
    TAGNAME := $(NAME)-$(VERSION)
endif
SOURCEDIR := $(shell pwd)
ARCHIVE := $(TAGNAME).tar.bz2

CVSROOT = $(shell cat CVS/Root 2>/dev/null || :)

CVSTAG = $(NAME)-r$(subst .,-,$(VERSION))

FILES = pci.ids usb.ids oui.txt iab.txt pnp.ids

.PHONY: all install tag force-tag check commit create-archive archive srpm-x \
    clean clog new-pci-ids new-usb-ids new-oui new-iab new-pnp-ids

include Makefile.inc

all:

Makefile.inc: configure
	./configure
	@echo "$@ generated. Run the make again."
	@exit 1

install: Makefile.inc
	mkdir -p -m 755 $(DESTDIR)$(datadir)/$(NAME)
	for foo in $(FILES) ; do \
		install -m 644 $$foo $(DESTDIR)$(datadir)/$(NAME) ;\
	done
	mkdir -p -m 755 $(DESTDIR)$(libdir)/modprobe.d
	install -m 644 -T blacklist.conf $(DESTDIR)$(libdir)/modprobe.d/dist-blacklist.conf

commit:
	git commit -a ||:

tag:
	@git tag -s -m "Tag as $(TAGNAME)" $(TAGNAME)
	@echo "Tagged as $(TAGNAME)"

force-tag:
	@git tag -s -f $(TAGNAME)
	@echo "Tag forced as $(TAGNAME)"

changelog:
	@rm -f ChangeLog
	@(GIT_DIR=.git git log > .changelog.tmp && mv .changelog.tmp ChangeLog || rm -f .changelog.tmp) || (touch ChangeLog; echo 'git directory not found: installing possibly empty changelog.' >&2)

check:
	@[ -x /sbin/lspci ] && /sbin/lspci -i pci.ids > /dev/null || { echo "FAILURE: /sbin/lspci -i pci.ids"; exit 1; } && echo "OK: /sbin/lspci -i pci.ids"
	@./check-pci-ids.py || { echo "FAILURE: ./check-pci-ids.py"; exit 1; } && echo "OK: ./check-pci-ids.py"
	@echo -n "CHECK date of pci.ids: "; grep "Date:" pci.ids | cut -d ' ' -f 5
	@echo -n "CHECK date of usb.ids: "; grep "Date:" usb.ids | cut -d ' ' -f 6

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
	@rm -f $(NAME)-*.gz $(NAME)-*.src.rpm new-pnp.xlsx pnp.ids.txt

clog: hwdata.spec
	@sed -n '/^%changelog/,/^$$/{/^%/d;/^$$/d;s/%%/%/g;p}' $< | tee $@

download: new-usb-ids new-pci-ids new-oui new-iab new-pnp-ids

new-usb-ids:
	@curl -O http://www.linux-usb.org/usb.ids

new-pci-ids:
	@curl -O http://pciids.sourceforge.net/pci.ids

new-oui:
	@curl -O http://standards.ieee.org/develop/regauth/oui/oui.txt

new-iab:
	@curl -O http://standards.ieee.org/develop/regauth/iab/iab.txt

new-pnp-ids: pnp.ids

pnp.ids: pnp.ids.txt pnp.ids.patch
	patch -o $@ <pnp.ids.patch

pnp.ids.txt: new-pnp.xlsx
	@unoconv --stdout -f csv $? | \
	    tr ' ' ' ' | \
	    sed -n \
		-e 's/^\s*"\s*\(.*\)\s*"/\1/' \
		-e 's/\s\{2,\}/ /g' \
		-e 's/\s*(used as 2nd pnpid)\s*//' \
		-e 's:^\(.*\)\s*,\s*\([a-zA-Z@]\{3\}\)\s*,\s*\([0-9]\+/[0-9]\+/[0-9]\+\):\2\t\1:p' | \
	    sed 's/\s*$$//' | sort -u >$@

new-pnp.xlsx:
	@curl -o $@ \
	    http://download.microsoft.com/download/7/E/7/7E7662CF-CBEA-470B-A97E-CE7CE0D98DC2/ISA_PNPID_List.xlsx
