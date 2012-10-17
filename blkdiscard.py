#! /usr/bin/env python

"""
Zero out a device under Linux by discarding the contents
"""

import sys
import os
import fcntl
import struct
import getopt

BLKGETSIZE64 = 0x80081272
BLKDISCARD = 0x1277
BLKDISCARDZEROES = 0x127c

USAGE = """
Usage: blkdiscard [-q] device

Discards the entire contents of DEVICE using the BLKDISCARD ioctl, as if it
were ovewritten with zeroes. Supported devices may include SSDs, memory cards,
and other flash storage devices, as well as network storage or volume
management systems with "thin provisioning" features.

THIS WILL PERMANENTLY DESTROY ALL CONTENTS OF THE DEVICE. YHBW. HTH. HAND.
"""

def usage(msg=None):
    out = sys.stderr if msg else sys.stdout
    if msg:
        print >>out, "Error:", msg
        print >>out
    print >>out, USAGE.strip()
    sys.exit(1 if msg else 0)

def msg(fmt, *args):
    if not quiet:
        sys.stdout.write(fmt % args)

def ioctl(fd, req, fmt, *args):
    buf = struct.pack(fmt, *(args or [0]))
    buf = fcntl.ioctl(fd, req, buf)
    return struct.unpack(fmt, buf)[0]

def main(args):
    opts, args = getopt.gnu_getopt(args, 'qh')
    if ('-h', '') in opts:
        usage()
    global quiet
    quiet = ('-q', '') in opts
    if not args:
        usage("Missing block device argument")
    elif len(args) > 2:
        usage("Only one device argument allowed")

    with open(args[0], 'w') as dev:
        fd = dev.fileno()
        size = ioctl(fd, BLKGETSIZE64, 'L')
        ioctl(fd, BLKDISCARDZEROES, 'I')
        # TODO: discard in segments and display progress
        ioctl(fd, BLKDISCARD, 'LL', 0, size)


if __name__ == "__main__":
    main(sys.argv[1:])