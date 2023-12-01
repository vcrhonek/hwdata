NAME=hwdata
VERSION=$(shell awk '/Version:/ { print $$2 }' hwdata.spec)
RELEASE=$(shell rpm -q --define 'dist %{nil}' --specfile --qf "%{release}" hwdata.spec)
ifeq ($(shell git rev-parse --abbrev-ref HEAD | sed -n 's/^\([^0-9-]\+\).*/\L\1/p'), rhel)
    # add revision to tag name for rhel branches
    TAGNAME := v$(VERSION)-$(RELEASE)
else
    TAGNAME := v$(VERSION)
endif
SOURCEDIR := $(shell pwd)
ARCHIVE := $(TAGNAME).tar.bz2

CVSROOT = $(shell cat CVS/Root 2>/dev/null || :)

CVSTAG = $(NAME)-r$(subst .,-,$(VERSION))

IDFILES = pci.ids usb.ids oui.txt iab.txt pnp.ids

# usb.ids is not in UTF-8
UTF_IDFILES = pci.ids oui.txt iab.txt pnp.ids

.PHONY: all install tag force-tag check commit create-archive archive srpm-x \
    clean clog download

include Makefile.inc

all:

Makefile.inc: configure
	./configure
	@echo "$@ generated. Run the make again."
	@exit 1

install: Makefile.inc
	mkdir -p -m 755 $(DESTDIR)$(datadir)/$(NAME)
	for foo in $(IDFILES) ; do \
		install -m 644 $$foo $(DESTDIR)$(datadir)/$(NAME) ;\
	done
	mkdir -p -m 755 $(DESTDIR)$(libdir)/modprobe.d
	install -m 644 -T blacklist.conf $(DESTDIR)$(libdir)/modprobe.d/dist-blacklist.conf

commit:
	git commit -vas ||:

tag:
	@git tag -s -m "Tag as $(TAGNAME)" $(TAGNAME)
	@echo "Tagged as $(TAGNAME)"

force-tag:
	@git tag -s -f -m "Tag as $(TAGNAME)" $(TAGNAME)
	@echo "Tag forced as $(TAGNAME)"

changelog:
	@rm -f ChangeLog
	@(GIT_DIR=.git git log > .changelog.tmp && mv .changelog.tmp ChangeLog || rm -f .changelog.tmp) || (touch ChangeLog; echo 'git directory not found: installing possibly empty changelog.' >&2)

check:
	@lspci -i pci.ids > /dev/null || { echo "FAILURE: lspci -i pci.ids"; exit 1; } && echo "OK: lspci -i pci.ids"
	@./check-pci-ids.py || { echo "FAILURE: ./check-pci-ids.py"; exit 1; } && echo "OK: ./check-pci-ids.py"
	@./check-usb-ids.sh
	@for file in $(UTF_IDFILES); do \
	    iconv -f UTF-8 "$$file" >/dev/null || { echo "FAILURE: $$file is not valid UTF-8 data"; exit 1; }; \
	    echo "OK: $$file is valid UTF-8 data"; \
	done
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

archive: check clean commit tag

upload:
	@scp $(ARCHIVE) fedorahosted.org:$(NAME)

srpm-x: create-archive
	@echo Creating $(NAME) src.rpm
	@rpmbuild --nodeps -bs --define "_sourcedir $(SOURCEDIR)" --define "_srcrpmdir $(SOURCEDIR)" $(NAME).spec
	@echo SRPM is: $(NAME)-$(VERSION)-$(RELEASE).src.rpm

clean:
	@rm -f $(NAME)-*.gz $(NAME)-*.src.rpm pnp.ids.csv \
	    *.downloaded *.utf8 *.orig

clog: hwdata.spec
	@sed -n '/^%changelog/,/^$$/{/^%/d;/^$$/d;s/%%/%/g;p}' $< | tee $@

download: $(IDFILES)

usb.ids.downloaded:
	@curl -o $@ http://www.linux-usb.org/usb.ids

pci.ids.downloaded:
	@curl -o $@ https://raw.githubusercontent.com/pciutils/pciids/master/pci.ids

oui.txt.downloaded:
	@curl -o $@ -O https://standards-oui.ieee.org/oui/oui.txt

iab.txt.downloaded:
	@curl -o $@ -O https://standards-oui.ieee.org/iab/iab.txt

pnp.ids.csv:
	@curl -o $@ \
	    https://uefi.org/uefi-pnp-export

usb.ids: usb.ids.utf8
	dos2unix -n $? $@

pci.ids: pci.ids.utf8
	dos2unix -n $? $@

oui.txt: oui.txt.utf8
	dos2unix -n $? $@

iab.txt: iab.txt.utf8
	dos2unix -n $? $@

pnp.ids.orig: pnp.ids.csv
	./process-pnp-ids.py $? $@

pnp.ids: pnp.ids.orig pnp.ids.patch
	patch -p1 -o $@ pnp.ids.orig pnp.ids.patch

%.utf8: %.downloaded
	@text=`LANG=C file $?`
	@encoding=`echo "$$text" | sed -n 's/.*\(iso-8859\S\*\|cp1[12]\d\+\).*/\1/Ip'`
	@if [ -n "$$encoding" ]; then \
	    iconv -f "$$encoding" -t UTF-8 $?; \
	else \
	    cat $?; \
	fi | sed 's/\s\+$$//' >$@

