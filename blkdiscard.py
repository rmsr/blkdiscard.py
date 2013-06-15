#! /usr/bin/env python

USAGE = """
Usage: blkdiscard [ -c SIZE ] DEVICE

Discards the entire contents of DEVICE using the BLKDISCARD ioctl, as if it
were ovewritten with zeroes. Supported devices may include SSDs, flash cards,
and other flash-based storage devices, as well as network storage or volume
management systems with "thin provisioning" features.

Flags:
    -c SIZE     Discard the device in chunks of SIZE megabytes, rather than
                all at once. Use this to prevent ioctl timeout errors if
                the discard operation is slow, such as with some SATA drives.

WARNING: THIS WILL PERMANENTLY ERASE THE ENTIRE CONTENTS OF YOUR DEVICE. YHBW.
"""

import sys
import os
import fcntl
import struct
import getopt

IOCTL_BLKGETSIZE64 = 0x80081272
IOCTL_BLKDISCARD = 0x1277
IOCTL_BLKDISCARDZEROES = 0x127c

def usage(msg=None):
    out = sys.stderr if msg else sys.stdout
    if msg:
        print >>out, "Error:", msg
        print >>out
    print >>out, USAGE.strip()
    sys.exit(1 if msg else 0)

def ioctl(fd, req, fmt, *args):
    buf = struct.pack(fmt, *(args or [0]))
    buf = fcntl.ioctl(fd, req, buf)
    return struct.unpack(fmt, buf)[0]

def discard_chunk(fd, offset, size):
    ioctl(fd, IOCTL_BLKDISCARD, 'LL', offset, size)

def discard(fd, chunksize):
    size = ioctl(fd, IOCTL_BLKGETSIZE64, 'L')
    ioctl(fd, IOCTL_BLKDISCARDZEROES, 'I')
    if not chunksize:
        discard_chunk(fd, 0, size)
        return
    for offset in xrange(0, size, chunksize):
        discard_chunk(fd, offset, min(chunksize, size, - offset))

def main(args):
    chunksize = 0
    helpopt = ( '-h', '' )
    opts, args = getopt.gnu_getopt(args, 'hc:')
    for flag, val in opts:
        if flag == '-h':
            usage()
        elif flag == '-c':
            try:
                chunksize = int(val)
                if chunksize < 1:
                    raise ValueError
            except ValueError:
                usage("Chunk size must be a positive nonzero integer")
            chunksize *= 1024 ** 2
    if len(args) != 1:
        usage("Exactly one device argument required")
    with open(args[0], 'w') as dev:
        discard(dev.fileno(), chunksize)

if __name__ == "__main__":
    main(sys.argv[1:])
