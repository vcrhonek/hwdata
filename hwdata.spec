Name: hwdata
Summary: Hardware identification and configuration data
Version: 0.146.33.EL
Release: 2
License: GPL/MIT
Group: System Environment/Base
Source: hwdata-%{version}-%{release}.tar.gz
BuildArch: noarch
Conflicts: Xconfigurator < 4.9.42-1, kernel-pcmcia-cs < 3.1.31-11, kudzu < 1.1.86
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

%description
hwdata contains various hardware identification and configuration data,
such as the pci.ids database, the XFree86 Cards and MonitorsDb databases.

%prep

%setup -q

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc LICENSE COPYING
%dir /usr/share/hwdata
%dir /etc/pcmcia
%config(noreplace) /etc/hotplug/blacklist
%config /etc/pcmcia/config
%config /usr/share/hwdata/*
# This file is screaming to be moved into /usr/share/hwdata sometime <g>
/usr/X11R6/lib/X11/Cards

%changelog
* Tue Apr 08 2008 Karsten Hopp <karsten@redhat.com> 0.146.33.EL-2
- unify MonitorsDB 
- update pci.ids, usb.ids, pcitable

* Thu Oct 25 2007 Phil Knirsch <pknirsch@redhat.com> 0.146.33.EL-1
- Map specific Intel network cards to the new e1000e driver (#253792)

* Wed Oct 17 2007 Karsten Hopp <karsten@redhat.com> 0.146.32.EL-1
- update pci.ids, usb.ids

* Thu Aug 30 2007 Karsten Hopp <karsten@redhat.com> 0.146.31.EL-1
- update pci.ids, usb.ids

* Thu Jul 26 2007 Karsten Hopp <karsten@redhat.com> 0.146.30.EL-1
- update pci.ids, usb.ids, fixes bz #229367

* Tue Jul 10 2007 Karsten Hopp <karsten@redhat.com> 0.146.29.EL-1
- fix usb.ids file
- Resolves: bz #233420

* Tue Jul 03 2007 Karsten Hopp <karsten@redhat.com> 0.146.29.EL-1
- make some network cards use the e1000 driver 
- Resolves: bz#206415

* Thu Mar 29 2007 Karsten Hopp <karsten@redhat.com> 0.146.28.EL-1
- fix pcitables entry for NVIDIA Quadro NVS 285

* Wed Mar 28 2007 Karsten Hopp <karsten@redhat.com> 0.146.27.EL-1
- update pcitables

* Wed Mar 28 2007 Karsten Hopp <karsten@redhat.com> 0.146.26.EL-1
- update pci.ids
- Resolves: #197012

* Mon Feb 12 2007 Karsten Hopp <karsten@redhat.com> 0.146.25.EL-1
- add HP TFT5600 monitor

* Mon Jan 29 2007 Soren Sandmann <sandmann@redhat.com> 0.146.25.EL-1
- update pcitable / Cards to support new XGI driver
- Related: #196785

* Fri Jan 19 2007 Karsten Hopp <karsten@redhat.com> 0.146.24.EL-3
- update pci.ids / usb.ids
- Resolves: #197012

* Mon Jan 08 2007 Karsten Hopp <karsten@redhat.com> 0.146.24.EL-2
- update pci.ids / usb.ids
- sync MonitorsDB between releases
- Resolves: #197070
- Resolves: #197792
- Resolves: #200734
- Resolves: #206458

* Mon Aug 28 2006 Phil Knirsch <pknirsch@redhat.com> 0.146.24.EL-1
- Included fix for Intel NIC issue for quad e1000 from Oracle on a Sun box

* Mon Aug 21 2006 Phil Knirsch <pknirsch@redhat.com> 0.146.23.EL-1
- Fixed regression in pcitable for QLA24x cards (#202267)

* Tue Jul 11 2006 Phil Knirsch <pknirsch@redhat.com> 0.146.22.EL-1
- Final pull of pci.ids and pcitable (#180521)

* Thu Jun 22 2006 Adam Jackson <ajackson@redhat.com> 0.146.21.EL-1
- Add Matrox G200e to Cards and pcitable

* Fri May 26 2006 Karsten Hopp <karsten@redhat.de> 0.146.20.EL-1
- add some monitors to MonitorsDB (#191693)

* Fri May 05 2006 Phil Knirsch <pknirsch@redhat.com> 0.146.19.EL-1
- Included pcitable update to support Nvidia FX3450 cards (#178462)
- Updated PCI ids from upstream (#180521)
- Fixed missing monitor entry in MonitorsDB (#189447)

* Fri Mar  3 2006 Bill Nottingham <notting@redhat.com> 0.146.18.EL-1
- blacklist EDAC modules (#183232)

* Thu Feb 09 2006 Phil Knirsch <pknirsch@redhat.com> 0.146.17.EL-1
- Added fix to detect the new ATI ES1000 chip properly (#180523)

* Fri Feb 03 2006 Phil Knirsch <pknirsch@redhat.com> 0.146.16.EL-1
- Fixed typo in upgradelist (#169783)

* Fri Jan 27 2006 Phil Knirsch <pknirsch@redhat.com> 0.146.15.EL-1
- Updated pci.ids according to our schedule (#179097)

* Thu Jan 19 2006 Phil Knirsch <pknirsch@redhat.com> 0.146.14.EL-1
- Fixed regression of missing line in pci.ids (#177169)

* Mon Nov 28 2005 Bill Nottingham <notting@redhat.com> 0.146.13.EL-1
- update pci.ids, usb.ids from upstream (#168602)
- add support for Intel 915/945 (#170517)

* Wed Aug 31 2005 Bill Nottingham <notting@redhat.com> 0.146.12.EL-1
- update pci.ids (#156948)

* Thu Aug 25 2005 Bill Nottingham <notting@redhat.com>
- /etc/pcmcia/config: fix typo (#166635)

* Thu Jul 21 2005 Bill Nottingham <notting@redhat.com> 0.146.11.EL-1
- update usb.ids, MonitorsDB (#158961)

* Tue Jul 19 2005 Bill Nottingham <notting@redhat.com>
- fix qlogic mapping

* Thu Jun 30 2005 Bill Nottingham <notting@redhat.com>
- add more mptfusion cards (#107088)

* Wed Jun 22 2005 Bill Nottingham <notting@redhat.com>
- add hisax modules to blacklist (#154799, #159068)

* Fri Jun 10 2005 Bill Nottingham <notting@redhat.com>
- fix ATI branding (#160047)

* Wed May  4 2005 Bill Nottingham <notting@redhat.com> 0.146.10.EL-1
- update pci.ids

* Fri Apr  8 2005 Mike A. Harris <mharris@redhat.com> 0.146.9.EL-1
- Updated Cards to change the default driver for Nvidia FX1400 or FX540 to
  "vesa" (#140601)

* Wed Mar 23 2005 Bill Nottingham <notting@redhat.com> 0.146.8.EL-1
- fix qla6322 mapping (correction of fix for #150621)

* Mon Mar 14 2005 Bill Nottingham <notting@redhat.com> 0.146.7.EL-1
- update pci.ids

* Wed Mar  9 2005 Bill Nottingham <notting@redhat.com> 0.146.6.EL-1
- fix qlaXXXX mappings, add migration entries (#150621)

* Mon Mar  7 2005 Bill Nottingham <notting@redhat.com> 0.146.5.EL-1
- more aic79xx entries (IT%67884)

* Wed Mar  2 2005 Mike A. Harris <mharris@redhat.com> 0.146.4.EL-1
- Bump and rebuild to fix build problem

* Wed Mar  2 2005 Mike A. Harris <mharris@redhat.com> 0.146.3.EL-1
- Added many new nvidia PCI IDs to pcitable and Cards to synchronize it
  with X.Org X11 6.8.2. (#140601)

* Tue Mar  1 2005 Bill Nottingham <notting@redhat.com> - 0.146.2.EL-1
- add sk98lin mapping (#145538)
- fix emu10k1x mapping (#147787)
- update usb.ids, pci.ids, MonitorsDB

* Wed Nov 10 2004 Bill Nottingham <notting@redhat.com> - 0.146.1.EL-1
- migrate dpt_i2o to i2o_block (#138603)

* Tue Nov  9 2004 Bill Nottingham <notting@redhat.com> - 0.146-1
- update pci.ids (#138233)
- add Apple monitors (#138481)

* Wed Oct 20 2004 Bill Nottingham <notting@redhat.com> - 0.145-1
- remove ahci mappings, don't prefer it over ata_piix

* Tue Oct 19 2004 Kristian Høgsberg <krh@redhat.com> - 0.144-1
- update IDs for Cirrus, Trident, C&T, and S3

* Tue Oct 12 2004 Bill Nottingham <notting@redhat.com> - 0.143-1
- add ahci mappings to prefer it over ata_piix
- map davej's ancient matrox card to vesa (#122750)

* Thu Oct  7 2004 Dan Williams <dcbw@redhat.com> - 0.141-1
- Add Belkin F5D6020 ver.2 (802.11b card based on Atmel chipset)

* Fri Oct  1 2004 Bill Nottingham <notting@redhat.com> - 0.140-1
- include /etc/hotplug/blacklist here

* Thu Sep 30 2004 Bill Nottingham <notting@redhat.com> - 0.136-1
- add S3 UniChrome (#131403)
- update pci.ids

* Thu Sep 23 2004 Bill Nottingham <notting@redhat.com> - 0.135-1
- megaraid -> megaraid_mbox

* Wed Sep 22 2004 Bill Nottingham <notting@redhat.com> - 0.134-1
- map ncr53c8xx to sym53c8xx (#133181)

* Fri Sep 17 2004 Bill Nottingham <notting@redhat.com> - 0.132-1
- fix 3Ware 9000 mapping (#132851)

* Tue Sep 14 2004 Kristian Høgsberg <krh@redhat.com> - 0.131-1
- Add python script to check sorting of pci.ids

* Thu Sep  9 2004 Kristian Høgsberg <krh@redhat.com> 0.131-1
- Add pci ids and cards for new ATI, NVIDIA and Intel cards

* Sat Sep  4 2004 Bill Nottingham <notting@redhat.com> 0.130-1
- trim pcitable - now just ids/drivers

* Wed Sep  1 2004 Bill Nottingham <notting@redhat.com> 0.125-1
- pci.ids updates
- remove updsftab.conf.*

* Sun Aug 29 2004 Mike A. Harris <mharris@redhat.com>  0.124-1
- Updates to pcitable/Cards for 'S3 Trio64 3D' cards. (#125866,59956)

* Fri Jul  9 2004 Mike A. Harris <mharris@redhat.com>  0.123-1
- Quick pcitable/Cards update for ATI Radeon and FireGL boards

* Mon Jun 28 2004 Bill Nottingham <notting@redhat.com>
- add Proview monitor (#125853)
- add ViewSonic monitor (#126324)
- add a Concord camera (#126673)

* Wed Jun 23 2004 Brent Fox <bfox@redhat.com> - 0.122-1
- Add Vobis monitor to MonitorsDB (bug #124151)

* Wed Jun 09 2004 Dan Williams <dcbw@redhat.com> - 0.121-1
- add Belkin F5D5020 10/100 PCMCIA card (#125581)

* Fri May 28 2004 Bill Nottingham <notting@redhat.com>
- add modem (#124663)

* Mon May 24 2004 Bill Nottingham <notting@redhat.com> - 0.120-1
- mainly:
  fix upgradelist module for CMPci cards (#123647)
- also:
  add another wireless card (#122676)
  add wireless card (#122625)
  add 1280x800 (#121548)
  add 1680x1050 (#121148)
  add IntelligentStick (#124313)

* Mon May 10 2004 Jeremy Katz <katzj@redhat.com> - 0.119-1
- veth driver is iseries_veth in 2.6

* Wed May  5 2004 Jeremy Katz <katzj@redhat.com> - 0.118-1
- add a wireless card (#122064)
- and a monitor (#121696)

* Fri Apr 16 2004 Bill Nottingham <notting@redhat.com> 0.117-1
- fix makefile

* Thu Apr 15 2004 Bill Nottingham <notting@redhat.com> 0.116-1
- move updfstab.conf here
- add wireless card (#116865)
- add laptop display panel (#117385)
- add clipdrive (#119928)
- add travelling disk (#119143)
- add NEXDISK (#106782)

* Thu Apr 15 2004 Brent Fox <bfox@redhat.com> 0.115-1
- replace snd-es1960 driver with snd-es1968 in pcitable (bug #120729)

* Mon Mar 29 2004 Bill Nottingham <notting@redhat.com> 0.114-1
- fix entries pointing to Banshee (#119388)

* Tue Mar 16 2004 Bill Nottingham <notting@redhat.com> 0.113-1
- add a Marvell sk98lin card (#118467, <64bit_fedora@comcast.net>)

* Fri Mar 12 2004 Brent Fox <bfox@redhat.com> 0.112-1
- add a Sun flat panel to MonitorsDB (bug #118138)

* Fri Mar  5 2004 Brent Fox <bfox@redhat.com> 0.111-1
- add Samsung monitor to MonitorsDB (bug #112112)

* Mon Mar  1 2004 Mike A. Harris <mharris@redhat.com> 0.110-1
- Added 3Dfx Voodoo Graphics and Voodoo II entries to the Cards database, both
  pointing to Alan Cox's new "voodoo" driver which is now included in XFree86
  4.3.0-62 and later builds in Fedora development.  Mapped their PCI IDs to
  the new Cards entry in pcitable.
- Updated the entries for 3Dfx Banshee

* Mon Feb 23 2004 Bill Nottingham <notting@redhat.com> 0.109-1
- pci.ids and other updates

* Thu Feb 19 2004 Mike A. Harris <mharris@redhat.com> 0.108-1
- Added Shamrock C407L to MonitorsDB for bug (#104920)

* Thu Feb 19 2004 Mike A. Harris <mharris@redhat.com> 0.107-1
- Massive Viewsonic monitor update for MonitorsDB (#84882)

* Fri Feb 13 2004 John Dennis <jdennis@finch.boston.redhat.com> 0.106-1
- fix typo, GP should have been HP

* Thu Jan 29 2004 Bill Nottingham <notting@redhat.com> 0.105-1
- many monitor updates (#114260, #114216, #113993, #113932, #113782,
  #113685, #113523, #111203, #107788, #106526, #63005)
- add some PCMCIA cards (#113006, #112505)

* Tue Jan 20 2004 Bill Nottingham <notting@redhat.com> 0.104-1
- switch sound module mappings to alsa drivers

* Mon Jan 19 2004 Brent Fox <bfox@redhat.com> 0.103-1
- fix tab spacing

* Fri Jan 16 2004 Brent Fox <bfox@redhat.com> 0.102-1
- added an entry for ATI Radeon 9200SE (bug #111306)

* Sun Oct 26 2003 Jeremy Katz <katzj@redhat.com> 0.101-1
- add 1920x1200 Generic LCD as used on some Dell laptops (#108006)

* Thu Oct 16 2003 Brent Fox <bfox@redhat.com> 0.100-1
- add entry for Sun (made by Samsung) monitor (bug #107128)

* Tue Sep 23 2003 Mike A. Harris <mharris@redhat.com> 0.99-1
- Added entries for Radeon 9600/9600Pro/9800Pro to Cards
- Fixed minor glitch in pcitable for Radeon 9500 Pro

* Tue Sep 23 2003 Jeremy Katz <katzj@redhat.com> 0.98-1
- add VMWare display adapter pci id and map to vmware X driver

* Thu Sep 11 2003 Bill Nottingham <notting@redhat.com> 0.97-1
- bcm4400 -> b44

* Sun Sep  7 2003 Bill Nottingham <notting@redhat.com> 0.96-1
- fix provided Dell tweaks (#103892)

* Fri Sep  5 2003 Bill Nottingham <notting@redhat.com> 0.95-1
- Dell tweaks (#103861)

* Fri Sep  5 2003 Bill Nottingham <notting@redhat.com> 0.94-1
- add adaptec pci id (#100844)

* Thu Sep  4 2003 Brent Fox <bfox@redhat.com> 0.93-1
- add an SGI monitor for bug (#74870)

* Wed Aug 27 2003 Bill Nottingham <notting@redhat.com> 0.92-1
- updates from sourceforge.net pci.ids, update pcitable accordingly

* Mon Aug 18 2003 Mike A. Harris <mharris@redhat.com> 0.91-1
- Added HP monitors for bug (#102495)

* Fri Aug 15 2003 Brent Fox <bfox@redhat.com> 0.90-1
- added a sony monitor (bug #101550)

* Tue Jul 15 2003 Bill Nottingham <notting@redhat.com> 0.89-1
- updates from modules.pcimap

* Sat Jul 12 2003 Mike A. Harris <mharris@redhat.com> 0.88-1
- Update MonitorsDB for new IBM monitors from upstream XFree86 bugzilla:
  http://bugs.xfree86.org/cgi-bin/bugzilla/show_bug.cgi?id=459

* Mon Jun  9 2003 Bill Nottingham <notting@redhat.com> 0.87-1
- fusion update

* Mon Jun  9 2003 Jeremy Katz <katzj@redhat.com> 0.86-1
- pci id for ata_piix

* Wed Jun  4 2003 Brent Fox <bfox@redhat.com> 0.85-1
- correct entry for Dell P991 monitor

* Tue Jun  3 2003 Bill Nottingham <notting@redhat.com> 0.84-1
- fix qla2100 mapping (#91476)
- add dell mappings (#84069)

* Mon Jun  2 2003 John Dennis <jdennis@redhat.com>
- Add new Compaq and HP monitors - bug 90570, bug 90707, bug 90575, IT 17231

* Wed May 21 2003 Brent Fox <bfox@redhat.com> 0.81-1
- add an entry for SiS 650 video card (bug #88271)

* Wed May 21 2003 Michael Fulbright <msf@redhat.com> 0.80-1
- Changed Generic monitor entries in MonitorsDB to being in LCD and CRT groups

* Tue May 20 2003 Bill Nottingham <notting@redhat.com> 0.79-1
- pci.ids and usb.ids updates

* Tue May  6 2003 Brent Fox <bfox@redhat.com> 0.78-1
- added a Samsung monitor to MonitorsDB

* Fri May  2 2003 Bill Nottingham <notting@redhat.com>
- add Xircom wireless airo_cs card (#90099)

* Fri Apr 18 2003 Jeremy Katz <katzj@redhat.com> 0.77-1
- add generic framebuffer to Cards

* Mon Mar 17 2003 Mike A. Harris <mharris@redhat.com> 0.76-1
- Updated MonitorsDb for Dell monitors (#86072)

* Tue Feb 18 2003 Mike A. Harris <mharris@redhat.com> 0.75-1
- Change savage MX and IX driver default back to "savage" for the 1.1.27t
  driver update
  
* Tue Feb 18 2003 Brent Fox <bfox@redhat.com> 0.74-1
- Use full resolution description for Dell laptop screens (bug #80398)

* Thu Feb 13 2003 Mike A. Harris <mharris@redhat.com> 0.73-1
- Updated pcitable and Cards database to fix Savage entries up a bit, and
  change default Savage/MX driver to 'vesa' as it is hosed and with no sign
  of working in time for 4.3.0.  Fixes (#72476,80278,80346,80423,82394)

* Wed Feb 12 2003 Brent Fox <bfox@redhat.com> 0.72-1
- slightly alter the sync rates for the Dell 1503FP (bug #84123)

* Tue Feb 11 2003 Bill Nottingham <notting@redhat.com> 0.71-1
- large pcitable and pci.ids updates
- more tg3, e100

* Mon Feb 10 2003 Mike A. Harris <mharris@redhat.com> 0.69-1
- Updated pcitable and Cards database for new Intel i852/i855/i865 support

* Mon Feb 10 2003 Mike A. Harris <mharris@redhat.com> 0.68-1
- Massive update of all ATI video hardware PCI IDs in pcitable and a fair
  number of additions and corrections to the Cards database as well
  
* Wed Jan 29 2003 Brent Fox <bfox@redhat.com> 0.67-1
- change refresh rates of sny0000 monitors to use a low common denominator

* Wed Jan 29 2003 Bill Nottingham <notting@redhat.com> 0.66-1
- don't force DRI off on R200 (#82957)

* Fri Jan 24 2003 Mike A. Harris <mharris@redhat.com> 0.65-1
- Added Card:S3 Trio64V2 (Unsupported RAMDAC) entry to pcitable, pci.ids, and
  Cards database to default this particular variant to "vesa" driver (#81659)

* Thu Jan  2 2003 Bill Nottingham <notting@redhat.com> 0.64-1
- pci.ids and associated pcitable updates

* Sun Dec 29 2002 Mike A. Harris <mharris@redhat.com> 0.63-1
- Updates for GeForce 2 Go, GeForce 4 (#80209)

* Thu Dec 12 2002 Jeremy Katz <katzj@redhat.com> 0.62-2
- fix Cards for NatSemi Geode

* Thu Dec 12 2002 Jeremy Katz <katzj@redhat.com> 0.62-1
- use e100 instead of eepro100 for pcmcia

* Mon Nov 25 2002 Mike A. Harris <mharris@redhat.com>
- Complete reconstruction of all Neomagic hardware entries in Cards
  database to reflect current XFree86, as well as pcitable update,
  and submitted cleaned up entries to sourceforge

* Mon Nov  4 2002 Bill Nottingham <notting@redhat.com> 0.61-1
- move pcmcia config file here
- sort MonitorsDB, add some entries, remove dups
- switch some network driver mappings

* Tue Sep 24 2002 Bill Nottingham <notting@redhat.com> 0.48-1
- broadcom 5704 mapping
- aic79xx (#73781)

* Thu Sep  5 2002 Bill Nottingham <notting@redhat.com> 0.47-1
- pci.ids updates
- add msw's wireless card

* Tue Sep  3 2002 Jeremy Katz <katzj@redhat.com> 0.46-1
- Card entries in pcitable need matching in Cards

* Sun Sep  1 2002 Mike A. Harris <mharris@redhat.com> 0.45-1
- Update G450 entry in Cards

* Tue Aug 13 2002 Bill Nottingham <notting@redhat.com> 0.44-1
- fix some of the Dell entries
- add cardbus controller id (#71198)
- add audigy mapping
- add NEC monitor (#71320)

* Tue Aug 13 2002 Preston Brown <pbrown@redhat.com> 0.43-1
- pci.id for SMC wireless PCI card (#67346)

* Sat Aug 10 2002 Mike A. Harris <mharris@redhat.com> 0.42-1
- Change default driver for old S3 based "Miro" card for bug (#70743)

* Fri Aug  9 2002 Preston Brown <pbrown@redhat.com> 0.41-1
- fix tabs in pci.ids
- Change pci ids for the PowerEdge 4 series again...

* Tue Aug  6 2002 Preston Brown <pbrown@redhat.com> 0.39-1
- Dell PERC and SCSI pci.id additions

* Tue Aug  6 2002 Mike A. Harris <mharris@redhat.com> 0.38-1
- Removed and/or invalid entries from Cards database BLOCKER (#70802)

* Mon Aug  5 2002 Mike A. Harris <mharris@redhat.com> 0.37-1
- Changed Matrox G450 driver default options to fix bug (#66697)
- Corrected S3 Trio64V2 bug in Cards file (#66492)

* Tue Jul 30 2002 Bill Nottingham <notting@redhat.com> 0.36-1
- tweaks for Dell Remote Assisstant cards (#60376)

* Thu Jul 26 2002 Mike A. Harris <mharris@redhat.com> 0.35-1
- Updated Cards db for CT69000
- Various ATI cleanups and additions to Cards and pcitable
- Updated S3 Trio3D to default to "vesa" driver (#59956)

* Tue Jul 23 2002 Bill Nottingham <notting@redhat.com> 0.33-1
- Eizo monitor updates (#56080, <triad@df.lth.se>)
- pci.ids updates, corresponding pcitable updates
- pcilint for pcitable 

* Fri Jun 28 2002 Bill Nottingham <notting@redhat.com> 0.32-1
- switch de4x5 back to tulip

* Mon Jun 24 2002 Mike A. Harris <mharris@redhat.com> 0.31-1
- Modified ATI entries in pcitable to be able to autodetect the FireGL 8700
  and FireGL 8800 which both have the same ID, but different subdevice ID's.
  Added entries to Cards database for the 8700/8800 as well.

* Tue May 28 2002 Mike A. Harris <mharris@redhat.com> 0.30-1
- Reconfigured Cards database to default to XFree86 4.x for ALL video
  hardware, since 3.3.6 support is being removed.  Video cards not
  supported natively by 4.x will be changed to use the vesa or vga
  driver, or completely removed as unsupported.

* Tue Apr 17 2002 Michael Fulbright <msf@redhat.com> 0.14-1
- another megaraid variant

* Mon Apr 15 2002 Michael Fulbright <msf@redhat.com> 0.13-1
- fix monitor entry for Dell 1600X Laptop Display Panel

* Fri Apr 12 2002 Bill Nottingham <notting@redhat.com> 0.13-1
- more aacraid

* Tue Apr  9 2002 Bill Nottingham <notting@redhat.com> 0.12-1
- another 3ware, another megaraid

* Fri Apr  5 2002 Mike A. Harris <mharris@redhat.com> 0.11-1
- Added commented out line for some Radeon 7500 cards to Cards database.

* Tue Apr  2 2002 Mike A. Harris <mharris@redhat.com> 0.10-1
- Fixed i830 entry to use driver "i810" not "i830" which doesn't exist

* Mon Apr  1 2002 Bill Nottingham <notting@redhat.com> 0.9-1
- fix rebuild (#62459)
- SuperSavage ids (#62101)
- updates from pci.ids

* Mon Mar 18 2002 Bill Nottingham <notting@redhat.com> 0.8-2
- fix errant space (#61363)

* Thu Mar 14 2002 Bill Nottingham <notting@redhat.com> 0.8-1
- nVidia updates

* Wed Mar 13 2002 Bill Nottingham <notting@redhat.com> 0.7-1
- lots of pcitable updates

* Tue Mar  5 2002 Mike A. Harris <mharris@redhat.com> 0.6-1
- Updated Cards database

* Mon Mar  4 2002 Mike A. Harris <mharris@redhat.com> 0.5-1
- Built new package with updated database files for rawhide.

* Fri Feb 22 2002 Bill Nottingham <notting@redhat.com> 0.3-1
- return of XFree86-3.3.x

* Wed Jan 30 2002 Bill Nottingham <notting@redhat.com> 0.1-1
- initial build
