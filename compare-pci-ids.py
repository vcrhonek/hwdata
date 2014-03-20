#!/usr/bin/env python

import argparse
import re
import sys

re_vendor = re.compile(r'^(?P<vendor_id>[0-9a-fA-F]{4})\s*(?P<vendor_name>.*)')
re_vendev = re.compile(r'^\s*(?P<vendor_id>[0-9a-fA-F]{4})\s+'
        r'(?P<device_id>[0-9a-fA-F]{4})\s+(?P<device_name>.*)')
re_device = re.compile(r'^\s+(?P<device_id>[0-9a-fA-F]{4})\s+'
        r'(?P<device_name>.*)')
re_comment = re.compile(r'^(\s*#.*|\s*)$')

def x2int(x):
    if isinstance(x, basestring): return int(x, 16)
    return x

def parse_pci_file(ids_file, file_name):
    """
    @return dictionary in format:
        { vendor_id: ( vendor_name
                     , { device_id : device_name
                       , ... }
                     )
        , ...
        }
      where
        vendor_id and device_id are integers
    """
    res = {}
    vendor = None
    nested = {} # (vendor_id, {device_id, device_name})

    def _add_nested(file_name, line, vendor, dev_id, dev_name):
        dev_id = x2int(dev_id)
        if vendor not in nested:
            nested[vendor] = {}
        if dev_id in nested[vendor]:
            sys.stderr.write('Warning: device "%04x:%04x" redeclared!'
            ' File: %s : %d\n'%(vendor, dev_id, file_name, line))
        nested[vendor][dev_id] = dev_name

    def _add_vendor(file_name, line, vendor_id, vendor_name):
        vendor = x2int(vendor_id)
        if vendor in res:
            sys.stderr.write('Warning: vendor "%04x" redeclared!'
                ' File: %s : %d\n'%(vendor, file_name, line))
            res[vendor] = (vendor_name, res[vendor][1])
        else:
            res[vendor] = (vendor_name, {})
            if vendor in nested:
                for dev_id, dev_name in nested[vendor].items():
                    _add_device(file_name, line,
                            vendor, dev_id, dev_name)
                del nested[vendor]

    def _add_device(file_name, line, vendor, dev_id, dev_name):
        """ @note: does not check for a vendor """
        dev_id = x2int(dev_id)
        if dev_id in res[vendor][1]:
            sys.stderr.write('Warning: device "%04x:%04x" redeclared!'
                ' File: %s : %d\n'%(vendor, dev_id, file_name, i))
        res[vendor][1][dev_id] = dev_name

    for i, l in enumerate(ids_file.readlines(), 1):
        if re_comment.match(l): continue
        m = re_vendor.match(l)
        if m:
            vendor = x2int(m.group('vendor_id'))
            _add_vendor(file_name, i, vendor, m.group('vendor_name'))
            continue

        m = re_vendev.match(l)
        if m:
            dev_vendor = x2int(m.group('vendor_id'))
            dev_id = x2int(m.group('device_id'))
            if vendor != dev_vendor and dev_vendor not in res:
                #sys.stderr.write('Warning: nested vendor of device "%x:%x"'
                #' does not match top level vendor "%x"! File: %s : %d\n' %(
                #dev_vendor, dev_id, vendor, file_name, i))
                _add_nested(file_name, i,
                        dev_vendor, dev_id, m.group('device_name'))
            else:
                _add_device(file_name, i,
                        dev_vendor, dev_id, m.group('device_name'))
            continue

        m = re_device.match(l)
        if m:
            _add_device(file_name, i,
                    vendor, m.group('device_id'), m.group('device_name'))
        else:
            sys.stderr.write("Warning: not handled line: \"%s\"\n" % l[:-1])

    for vendor, devices in nested.items():
        sys.stderr.write('Warning: no name for vendor "%04x"! File: %s\n'%(
            vendor, file_name))
        res[vendor] = ('<UNKNOWN>', devices)
    return res

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Compare new pci.ids to old.")
    parser.add_argument('old', type=argparse.FileType('r'),
            help="old pci.ids file")
    parser.add_argument('new', type=argparse.FileType('r'),
            help="new pci.ids file")

    args = parser.parse_args()
    old = parse_pci_file(args.old, args.old.name)
    new = parse_pci_file(args.new, args.new.name)
    
    vendors_removed = 0
    vendors_added = 0
    vendors_renamed = 0
    devices_removed = 0
    devices_added = 0
    devices_renamed = 0
    for vendor, (vendor_name, devices) in old.items():
        if vendor not in new:
            vendors_removed += 1
            devices_removed += len(devices)
        else:
            if vendor_name != new[vendor][0]:
                vendors_renamed += 1
            for dev_id, dev_name in devices.items():
                if dev_id not in new[vendor]:
                    devices_removed += 1
                elif dev_name != new[vendor][dev_id]:
                        devices_renamed += 1

    for vendor, (vendor_name, devices) in new.items():
        if vendor not in old:
            vendors_added += 1
            devices_added += len(devices)
        else:
            for dev_id, dev_name in devices.items():
                if dev_id not in old[vendor]:
                    devices_added += 1

    print "old vendor count: %d" % len(old)
    print "new vendor count: %d" % len(new)
    print "vendors added:    %d" % vendors_added
    print "vendors removed:  %d" % vendors_removed
    print "vendors renamed:  %d" % vendors_renamed
    print "devices added:    %d" % devices_added
    print "devices removed:  %d" % devices_removed
    print "devices renamed:  %d" % devices_renamed

    sys.exit(0)

