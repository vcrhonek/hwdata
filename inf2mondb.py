#!/usr/bin/python
#
# inf2mondb.py: convert MicroSoft .inf files for monitors to MonitorDB
#
# Matt Wilson <msw@redhat.com>
#
# Copyright 2002 Red Hat, Inc.
#
# This software may be freely redistributed under the terms of the GNU
# library public license.
#
# You should have received a copy of the GNU Library Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


import sys
import string
import re

def usage():
    print "Usage: inf2mondb.py filename.inf"
    sys.exit(1)

if len(sys.argv) < 2:
    usage()

try:
    f = open(sys.argv[1], 'r')
except IOError, (errno, str):
    print "Unable to open %s: %s" % (sys.argv[1], str)
    sys.exit(1)

lines = f.readlines()
f.close()

# the current section
section = None
# monitors - a dictionary keyed off manufacturers
monitors = {}
# a dictionary of manufacturers we're looking at
manufacturers = {}
# registry sections mapped back to the install sections
regsections = {}
# install sections that map back to monitor definitions
instsections = {}
# a big fat dictionary of strings to use later on.
strings = {}

class Monitor:
    def __repr__(self):
        return "%s; %s; %s; %s; %s" % (self.man,
                                       self.descr,
                                       self.edid,
                                       self.hsync,
                                       self.vsync)
    
    def __init__(self, man, id, edid):
        self.descr = ""
        self.man = man
        self.hsync = ""
        self.vsync = ""
        self.id = id
        self.edid = edid

sectRe = re.compile(r'\[*\]')
sectSplit = re.compile(r'[\[\]]')
infoSplit = re.compile(r'[%=\\;]')
# This RE is for EISA info lines
# %D5259A%=D5259A, Monitor\HWP0487
monitor1Re = re.compile(r'%*.%.*=.*,.*Monitor\\')
# This one is for legacy entries
# %3020%     =PB3020,	MonID_PB3020
monitor2Re = re.compile(r'%*.%.*=.*,.*MonID_')

for line in lines:
    tmp = string.strip(line)
    if tmp and tmp[0] == ';':
        continue
    if sectRe.search (line, 1):
        section = string.lower(sectSplit.split (line)[1])
        continue
    if section == "manufacturer":
        tmp = infoSplit.split (line)
        if len(tmp) > 1:
            manufacturer = string.lower(tmp[1])
            if manufacturers.has_key (tmp[1]):
                raise RuntimeError, "Duplicate manufacturer entries"
            else:
                manufacturers[string.lower(string.strip(tmp[3]))] = string.lower(string.strip(tmp[1]))
    # if we're in a manufacturer section, we need to jot down
    # the devices
    elif manufacturers.has_key(section):
        # Find monitor inf IDs and EISA ids:
        monre = None
        # EISA entries
        # %D5259A%=D5259A, Monitor\HWP0487
        if monitor1Re.search(line, 1):
            monre = monitor1Re
        # older non EISA entries
        # %3020%     =PB3020,	MonID_PB3020
        elif monitor2Re.search(line, 1):
            monre = monitor2Re
        if monre:
            end = monre.search(line, 1).end()
            id = string.strip(string.split(line, '%')[1])

            if monre == monitor1Re:
                # all EDID ID strings are 7 chars
                edid = string.strip(line[end:])[0:7]
            else:
                edid = "0"

            # we need to get the install section for this device
            rhs = string.strip(string.split (line, '=')[1])
            install = string.lower(string.strip(string.split (rhs, ',')[0]))
            if instsections.has_key (install):
                instsections[install].append ((section, id))
            else:
                instsections[install] = [ (section, id) ]

            if not monitors.has_key (section):
                monitors[section] = {}
            monitors[section][id] = Monitor(section, id, edid)
    elif section == "strings":
        tmp = string.strip(tmp)
        if not tmp:
            continue
        tmp = string.split (line, '=')
        if len (tmp) < 2:
            continue
        key = string.lower(string.strip(tmp[0]))
        tmp = string.split(string.strip(tmp[1]), '"')
        if len (tmp) > 1:
            value = tmp[1]
        else:
            value = tmp[0]
        strings[key] = string.strip(value)
    # these are the sections that tell us which AddReg to use
    # AddReg=PBCOM14L.AddReg, 1024, DPMS
    elif instsections.has_key(section):
        if string.find (line, "AddReg=") >= 0:
            rhs = string.split (line, '=')[1]
            # PBCOM14L.AddReg, 1024, DPMS
            registry = string.lower(string.strip(string.split(rhs, ',')[0]))
            # add this monitor to the list of monitors that will
            # use this registry entry
            if regsections.has_key(registry):
                regsections[registry].append (section)
            else:
                regsections[registry] = [ section ]
    # these are the actual AddReg entries.  Look up in our table
    # to find which
    elif regsections.has_key(section):
        if string.find(line, 'HKR,"MODES') >= 0:
            ids = regsections[section]
            # make a list of all the monitors pointing to
            # this registry section via install sections
            mons = []
            for id in ids:
                mons = mons + instsections[id]
            modes = string.split(line, '"')
            sync = string.split(modes[3], ',')
            for (man, mon) in mons:
                monitors[man][mon].hsync = string.strip(sync[0])
                monitors[man][mon].vsync = string.strip(sync[1])

for man in manufacturers.keys():
    for monitor in monitors[man].values():
        # OK, I know it's hacked up to look up these strings way down
        # here, but .inf format is CRAP.
        try:
            monitor.descr = strings[string.lower(monitor.id)]
        except KeyError:
            monitor.descr = monitor.id
        try:
            monitor.man = strings[string.lower(manufacturers[man])]
        except:
            monitor.man = manufacturers[man]
            
        print monitor

        
    
