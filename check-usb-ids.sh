#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

if [[ "${NO_DOCKER:-0}" == 1 ]]; then
    echo "SKIP: usb ids because of disabled docker test"
    exit 0
fi

tmpdir=`mktemp -d`
echo "Listing usb devices:"
sudo podman run -t --privileged --rm=true \
    -v `pwd`/usb.ids:/usr/share/hwdata/usb.ids:ro \
    -v "$tmpdir:/mnt/out" \
    vcrhonek/hwdata-check \
    /bin/bash -c 'lsusb 2>/mnt/out/err.out; python3 /usr/share/doc/python3-hwdata/example.py 2>>/mnt/out/err.out' || :
if [[ `cat $tmpdir/err.out | wc -l` -gt 0 ]]; then
    echo "ERRORS:"
    nl $tmpdir/err.out
    rm -rf $tmpdir
    exit 1
fi
rm -rf $tmpdir
