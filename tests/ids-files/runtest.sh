#!/bin/bash
# vim: dict=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   runtest.sh of /kernel/hwdata/Sanity/ids-files
#   Description: compares upstream ID files with our ID files
#   Author: Milos Malik <mmalik@redhat.com>
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Copyright (c) 2009 Red Hat, Inc. All rights reserved.
#
#   This copyrighted material is made available to anyone wishing
#   to use, modify, copy, or redistribute it subject to the terms
#   and conditions of the GNU General Public License version 2.
#
#   This program is distributed in the hope that it will be
#   useful, but WITHOUT ANY WARRANTY; without even the implied
#   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#   PURPOSE. See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public
#   License along with this program; if not, write to the Free
#   Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
#   Boston, MA 02110-1301, USA.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Include rhts environment
. /usr/share/beakerlib/beakerlib.sh || exit 1

PACKAGE="hwdata"
HWDATA_DIR="/usr/share/hwdata"
PCI_IDS_FILE="pci.ids"
PCI_IDS_URL="https://raw.githubusercontent.com/pciutils/pciids/master/pci.ids"
USB_IDS_FILE="usb.ids"
USB_IDS_URL="http://www.linux-usb.org/usb.ids"

rlJournalStart
    rlPhaseStartSetup
        rlAssertRpm ${PACKAGE}
        rlIsFedora ">39" && rlAssertRpm wget2 || rlAssertRpm wget
        rlAssertExists ${HWDATA_DIR}/${PCI_IDS_FILE}
        rlAssertExists ${HWDATA_DIR}/${USB_IDS_FILE}
    rlPhaseEnd

    rlPhaseStartTest
        rlRun "wget -q -t 4 ${PCI_IDS_URL}"
        rlAssertExists ${PCI_IDS_FILE}
        echo "Lines in upstream file: "`wc -l < ${PCI_IDS_FILE}`
        echo "Lines in our file: "`wc -l < ${HWDATA_DIR}/${PCI_IDS_FILE}`
        echo "Common lines: "`comm -1 -2 ${PCI_IDS_FILE} ${HWDATA_DIR}/${PCI_IDS_FILE} | wc -l`
        echo "Different lines in upstream file: "`comm -2 -3 ${PCI_IDS_FILE} ${HWDATA_DIR}/${PCI_IDS_FILE} | wc -l`
        echo "Different lines in our file: "`comm -1 -3 ${PCI_IDS_FILE} ${HWDATA_DIR}/${PCI_IDS_FILE} | wc -l`

        rlRun "wget -q -t 4 ${USB_IDS_URL}"
        rlAssertExists ${USB_IDS_FILE}
        echo "Lines in upstream file: "`wc -l < ${USB_IDS_FILE}`
        echo "Lines in our file: "`wc -l < ${HWDATA_DIR}/${USB_IDS_FILE}`
        echo "Common lines: "`comm -1 -2 ${USB_IDS_FILE} ${HWDATA_DIR}/${USB_IDS_FILE} | wc -l`
        echo "Different lines in upstream file: "`comm -2 -3 ${USB_IDS_FILE} ${HWDATA_DIR}/${USB_IDS_FILE} | wc -l`
        echo "Different lines in our file: "`comm -1 -3 ${USB_IDS_FILE} ${HWDATA_DIR}/${USB_IDS_FILE} | wc -l`
    rlPhaseEnd

    rlPhaseStartCleanup
        rlRun "rm -f ${PCI_IDS_FILE}"
        rlRun "rm -f ${USB_IDS_FILE}"
    rlPhaseEnd
rlJournalPrintText
rlJournalEnd

