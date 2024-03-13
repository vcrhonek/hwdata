#!/usr/bin/env python

import re
import sys

# Check that the sorting order is preserved in pci.ids

vendor_id = None
device_id = None
lineno    = 1

file = open("pci.ids")
hexnum = '([0-9a-fA-F]{4})'
desc = '(.*\\S)'

for line in file:

    m = re.match(hexnum + '\\s+' + desc, line)
    if m:
        new_id = int('0x' + m.group (1), 16)
        if vendor_id is not None and new_id <= vendor_id:
            print ("%d: Vendor ID (0x%04x) is less that previous ID (0x%04x)" %
                   (lineno, new_id, vendor_id))
            sys.exit (-1)

        vendor_id = new_id
        device_id = -1

    m = re.match('\t' + hexnum + '\\s+' + desc, line)
    if m:
        new_id = int('0x' + m.group (1), 16)
        if new_id <= device_id:
            print ("%d: Device ID (0x%04x) is less that previous ID (0x%04x)" %
                   (lineno, new_id, device_id))
            sys.exit (-1)

        device_id = new_id

    lineno = lineno + 1
