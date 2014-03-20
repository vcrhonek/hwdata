NAME=hwdata
VERSION=$(shell awk '/Version:/ { print $$2 }' hwdata.spec)
RELEASE=$(shell rpm -q --define 'dist %{nil}' --specfile --qf "%{release}" hwdata.spec)
SOURCEDIR := $(shell pwd)

include Makefile.inc

CVSROOT = $(shell cat CVS/Root 2>/dev/null || :)

CVSTAG = $(NAME)-r$(subst .,-,$(VERSION))

FILES = pci.ids usb.ids oui.txt pnp.ids

.PHONY: all install tag force-tag check commit create-archive archive srpm-x \
    clean clog new-pci-ids new-usb-ids new-pnp-ids

all: 

install:
	mkdir -p -m 755 $(DESTDIR)$(datadir)/$(NAME)
	for foo in $(FILES) ; do \
		install -m 644 $$foo $(DESTDIR)$(datadir)/$(NAME) ;\
	done
	mkdir -p -m 755 $(DESTDIR)$(prefix)/lib/modprobe.d
	install -m 644 -T blacklist.conf $(DESTDIR)$(prefix)/lib/modprobe.d/dist-blacklist.conf

commit:
	git commit -a ||:

tag:
	@git tag -a -m "Tag as $(NAME)-$(VERSION)-$(RELEASE)" $(NAME)-$(VERSION)-$(RELEASE)
	@echo "Tagged as $(NAME)-$(VERSION)-$(RELEASE)"

force-tag:
	@git tag -f $(NAME)-$(VERSION)-$(RELEASE)
	@echo "Tag forced as $(NAME)-$(VERSION)-$(RELEASE)"

changelog:
	@rm -f ChangeLog
	@(GIT_DIR=.git git log > .changelog.tmp && mv .changelog.tmp ChangeLog || rm -f .changelog.tmp) || (touch ChangeLog; echo 'git directory not found: installing possibly empty changelog.' >&2)

check:
	@[ -x /sbin/lspci ] && /sbin/lspci -i pci.ids > /dev/null || { echo "FAILURE: /sbin/lspci -i pci.ids"; exit 1; } && echo "OK: /sbin/lspci -i pci.ids"
	@./check-pci-ids.py || { echo "FAILURE: ./check-pci-ids.py"; exit 1; } && echo "OK: ./check-pci-ids.py"
	@echo -n "CHECK date of pci.ids: "; grep "Date:" pci.ids | cut -d ' ' -f 5
	@echo -n "CHECK date of usb.ids: "; grep "Date:" usb.ids | cut -d ' ' -f 6

create-archive:
	@rm -rf $(NAME)-$(VERSION) $(NAME)-$(VERSION).tar*  2>/dev/null
	@make changelog
	@git archive --format=tar --prefix=$(NAME)-$(VERSION)/ HEAD > $(NAME)-$(VERSION).tar
	@mkdir $(NAME)-$(VERSION)
	@cp ChangeLog $(NAME)-$(VERSION)/
	@tar --append -f $(NAME)-$(VERSION).tar $(NAME)-$(VERSION)
	@bzip2 -f $(NAME)-$(VERSION).tar
	@rm -rf $(NAME)-$(VERSION)
	@echo ""
	@echo "The final archive is in $(NAME)-$(VERSION).tar.bz2"

archive: check clean commit tag create-archive

upload:
	@scp ${NAME}-$(VERSION).tar.bz2 fedorahosted.org:$(NAME)

dummy:

srpm-x: create-archive
	@echo Creating $(NAME) src.rpm
	@rpmbuild --nodeps -bs --define "_sourcedir $(SOURCEDIR)" --define "_srcrpmdir $(SOURCEDIR)" $(NAME).spec
	@echo SRPM is: $(NAME)-$(VERSION)-$(RELEASE).src.rpm

clean:
	@rm -f $(NAME)-*.gz $(NAME)-*.src.rpm new-pnp.xlsx pnp.ids.txt

clog: hwdata.spec
	@sed -n '/^%changelog/,/^$$/{/^%/d;/^$$/d;s/%%/%/g;p}' $< | tee $@

download: new-usb-ids new-pci-ids new-oui.txt new-pnp-ids

new-usb-ids:
	@curl -O http://www.linux-usb.org/usb.ids

new-pci-ids:
	@curl -O http://pciids.sourceforge.net/pci.ids

new-oui.txt:
	@curl -O http://standards.ieee.org/develop/regauth/oui/oui.txt

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
