"""
Created on Mon Jun 14 15:22:08 2021

Represents a minimalistic Bitcoin script serializer.
Even though Bitcoin supports many op codes (https://en.bitcoin.it/wiki/Script), I only use what I need.

@author: tj
"""

import struct
from binascii import unhexlify, hexlify

DEFAULT_TX_SEQUENCE = b'\xff\xff\xff\xff'

BTC_OP_CODES = {
    'OP_0': b'\x00',
    'OP_DUP': b'\x76',
    'OP_HASH160': b'\xa9',
    'OP_EQUALVERIFY': b'\x88',
    'OP_CHECKSIG': b'\xac',
    'OP_EQUAL': b'\x87',
    'OP_RETURN': b'\x6a'
}


class BTCScript:
    def __init__(self, script):
        self.script = script

    def op_push_data(self, data):
        data_bytes = unhexlify(data)

        if len(data_bytes) < 0x4c:
            return chr(len(data_bytes)).encode() + data_bytes
        elif len(data_bytes) < 0xff:
            return b'\x4c' + chr(len(data_bytes)).encode() + data_bytes
        elif len(data_bytes) < 0xffff:
            return b'\x4d' + struct.pack('<H', len(data_bytes)) + data_bytes
        elif len(data_bytes) < 0xffffffff:
            return b'\x4e' + struct.pack('<I', len(data_bytes)) + data_bytes
        else:
            raise ValueError("Data too large")

    def prepend_compact_size(self, data):
        prefix = b''
        size = len(data)
        if 0 <= size <= 252:
            prefix = unhexlify(format(size, '02x').encode())
        elif 253 <= size <= 0xffff:
            prefix = b'\xfd' + unhexlify(format(size, '04x'))[::-1]
        elif 0x10000 <= size <= 0xffffffff:
            prefix = b'\xfe' + unhexlify(format(size, '08x'))[::-1]
        elif 0x100000000 <= size <= 0xffffffffffffffff:
            prefix = b'\xff' + unhexlify(format(size, '016x'))[::-1]
        else:
            raise ValueError("Data size not between 0 and 0xffffffffffffffff")

        return prefix + data

    def segwit_push_data(self, data):
        data_bytes = unhexlify(data)
        return self.prepend_compact_size(data_bytes)

    def to_bytes(self, with_segwit=False):
        script_bytes = b''
        for token in self.script:
            if token in BTC_OP_CODES:
                script_bytes += BTC_OP_CODES[token]
            else:
                if with_segwit:
                    script_bytes += self.segwit_push_data(token)
                else:
                    script_bytes += self.op_push_data(token)

        return script_bytes

    def __str__(self):
        return str(self.script)

    def to_hex(self):
        b = self.to_bytes()
        return hexlify(b).decode('utf-8')
