#!/usr/bin/python
#
# inf2mondb.py: convert MicroSoft .inf files for monitors to MonitorDB
#
# originally by Matt Wilson <msw@redhat.com>
# option parsing and database comparison by Fred New
# ini parsing completely rewritten by Matt Domsch <Matt_Domsch@dell.com> 2006
#
# Copyright 2002 Red Hat, Inc.
# Copyright 2006 Dell, Inc.
#
# This software may be freely redistributed under the terms of the GNU
# library public license.
#
# You should have received a copy of the GNU Library Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
"""


import sys
import string
import re
import ConfigParser

# this is a class to deal with various file line endings and leading whitespace
# converts all \r line endings to \n.
# It also strips leading whitespace.
# NOTE: be sure to always return _something_, even if it is just "\n", or we 
# break the file API.  (nothing == eof)
class myFile(object):
    def __init__(self, *args):
        self.fd = open(*args)

    def close(self):
        return self.fd.close()
    
    def readline(self, *args):
        line = self.fd.readline(*args)
        line = line.replace('\r', '\n')
        line = line.replace('\n\n', '\n')
        line = line.lstrip(" \t")
        return line


# we will use this to override default option parsing in ConfigParser to handle
# Microsoft-style "INI" files. (Which do not necessarily have " = value " after
# the option name
OPTCRE = re.compile(
        r'(?P<option>[^:=\s][^:=]*)'          # very permissive!
        r'\s*(?P<vi>[:=]{0,1})\s*'            # any number of space/tab,
                                              # optionally followed by
                                              # separator (either : or =)
                                              # optionally followed
                                              # by any # space/tab
        r'(?P<value>.*)$'                     # everything up to eol
        )

def usage():
    print "No monitor.inf file specified."
    sys.exit(1)
    
percentSplit = re.compile(r'%(?P<field>.*)%')
def percent_to_string(ini, strings, name):
    mo = percentSplit.match(name)
    if (mo):
        field = mo.group('field')
        try:
            val = strings[field.lower()]
        except KeyError:
            return ""
        return val.strip()
    return ""


def main():
    defaultDB = "/usr/share/hwdata/MonitorsDB"
    
    from optparse import OptionParser
    parser = OptionParser(usage= sys.argv[0] + " [options] filename.inf")
    parser.add_option("-n", "--new",
                    action="store_true", dest="newonly", default=False,
                    help="Compare results with the monitors database and only "
                        "show DB lines that don't already appear in the "
                        "database.")
    parser.add_option("-v", "--verbose",
                    action="store_true", dest="verbose", default=False,
                    help="Used with --new to permit us to see which monitors "
                        "already appear in the monitors database.")
    parser.add_option("-d", "--database",
                    dest="database",
                    default=defaultDB,
                    help="Used with --new to specify a different "
                        "monitors database.  "
                        "The default is " + defaultDB + ".",
                    metavar="FILE")
    parser.add_option("-i", "--inflist",
                    dest="inflist",
                    default=None,
                    help="Read list of inf files from inflist",
                    metavar="FILE")
    
    (options, args) = parser.parse_args()
    
    ini = ConfigParser.ConfigParser()
    ini.optionxform = __builtins__.str
    ini.OPTCRE = OPTCRE
    if options.inflist is not None:
        f = open(options.inflist)
        lines = f.readlines()
        f.close
        for a in lines:
            f = myFile(a.strip())
            ini.readfp(f)
            f.close

    for a in args:
        f = myFile(a)
        ini.readfp(f)
        f.close()

    # First, build a dictionary of monitors we already know about.
    # When we get ready to print the monitors we found in the .inf
    # file, we can decide whether it is new or not.
    
    # Dictionary of booleans showing whether certain monitor EDIDs are known.
    # knownids[knownID] = True
    # knownids[unknownID] isn't defined.
    knownids = {}
    
    if options.newonly:
        try:
            mdb = open(options.database, 'r')
        except IOError, (errno, str):
            print "Unable to open %s: %s" % (options.database, str)
            sys.exit(1)
    
        knowns = mdb.readlines()
        mdb.close()
    
        for known in knowns:
            if len(string.strip(known)) == 0 or known[0] == '#':
                continue
            knownids[string.lower(string.strip(string.split(known, ';')[2]))] = True
    

    # a dictionary of manufacturers we're looking at
    manufacturers = {}
    # a big fat dictionary of strings to use later on.
    strings = {}

    # This RE is for EISA info lines
    # %D5259A%=D5259A, Monitor\HWP0487
    monitor1Re = re.compile(r'.*,.*Monitor\\(?P<id>[^\s]*)')
    # This one is for legacy entries
    # %3020%     =PB3020,   MonID_PB3020
    monitor2Re = re.compile(r'.*,.*MonID_(?P<id>[^\s]*)')
    
    for section in ini.sections():
        if section.lower() == "manufacturer":
            for mfr in ini.options(section):
                # generate the vendor.arch funny entries
                manufacturer_values = string.split(ini.get(section, mfr), ',')
                manufacturers[manufacturer_values[0]] = mfr
                while len(manufacturer_values) > 1:
                    manufacturers["%s.%s" % (manufacturer_values[0], manufacturer_values[-1])] = mfr
                    manufacturer_values = manufacturer_values[0:-1]
    
        elif section.lower() == "strings":
            for key in ini.options(section):
                strings[key.lower()] = string.strip(ini.get(section, key)).replace('"','')
            # exceptions
            strings["dell"] = "Dell"
    
    
    for mfr in manufacturers.keys():
        if ini.has_section(mfr):
            monitor_vendor_name = manufacturers[mfr]
            for monitor_name in ini.options(mfr):
                v = ini.get(mfr, monitor_name)
                v = v.split(',')
                install_key = v[0].strip()
    
                line = ini.get(mfr, monitor_name)
                # Find monitor inf IDs and EISA ids
    
                edid = "0"
                mo = monitor1Re.match(line)
                if mo:
                    edid = mo.group('id')
                else:
                    mo = monitor2Re.match(line)
                    if mo:
                        edid = mo.group('id').strip()
    
                if knownids.has_key(edid.lower()):
                    continue
    
                if ini.has_section(install_key):
                    line = ini.get(install_key, "AddReg")
                    if line:
                        sline = line.split(',')
                        registry = sline[0]
                        try:
                            resolution = sline[1]
                        except IndexError:
                            resolution = ""
                        try:
                            dpms = sline[2]
                        except IndexError:
                            dpms = ""
    
                        if ini.has_section(registry):
                            for line in ini.options(registry):
                                if string.find(line, 'HKR,"MODES') >= 0:
                                    sline = line.split('"')
                                    try:
                                        syncline = sline[3]
                                    except IndexError:
                                        syncline = ","
                                        
                                    syncline = syncline.split(',')
                                    hsync = syncline[0].strip()
                                    vsync = syncline[1].strip()
    
                                    output = "%s; %s; %s; %s; %s" % (percent_to_string(ini, strings, monitor_vendor_name),
                                                                     percent_to_string(ini, strings, monitor_name),
                                                                     edid, hsync, vsync)
                                    if dpms.lower().strip() == "dpms":
                                        output = output + "; 1"
    
                                    if not knownids.has_key(edid.lower()):
                                        print output
                                        knownids[edid.lower()] = True



if __name__ == "__main__":
    sys.exit(main())
