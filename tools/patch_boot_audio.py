#!/usr/bin/env python3
"""Patch the supported stock Unisoc library to use media audio for boot only."""
import argparse
import hashlib
from pathlib import Path
import struct

STOCK_SHA256 = '39322942066577aa56d7119dbd7bfbd0f07e0e5c7965b42be33b8c23905f6a5b'
PATCHED_SHA256 = '7dc2c9f55fb466b05a50b6c4c098052a4a8187379699be577f6dc3606c28a47f'

def adr(register, pc, target):
    displacement = target-pc
    return 0x10000000 | ((displacement & 3) << 29) | (((displacement >> 2) & 0x7ffff) << 5) | register

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stock_library', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    data = bytearray(args.stock_library.read_bytes())
    if hashlib.sha256(data).hexdigest() != STOCK_SHA256:
        parser.error('Unsupported stock library; expected build1790133188')
    # Retain the Boot/Shutdown labels with ADR instead of ADRP+ADD, freeing
    # one instruction on each path to carry its stream across setDataSource.
    # w21 is callee-saved and is reset to the original return value at0x44ac.
    changes = {
        0x447c: (0xb0fffff4, adr(20, 0x447c, 0x1b69)),
        0x4480: (0x912da694, 0x52800035),  # Shutdown: STREAM_SYSTEM
        0x4488: (0xb0fffff4, adr(20, 0x4488, 0x1c12)),
        0x448c: (0x91304a94, 0x52800075),  # Boot: STREAM_MUSIC
        0x44a8: (0x52800021, 0x2a1503e1),  # mov w1,w21
    }
    for offset, (before, after) in changes.items():
        if struct.unpack_from('<I', data, offset)[0] != before:
            parser.error('Unexpected instruction at ' + hex(offset))
        struct.pack_into('<I', data, offset, after)
    assert hashlib.sha256(data).hexdigest() == PATCHED_SHA256
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)

if __name__ == '__main__':
    main()
