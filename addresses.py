"""
Created on Mon Jun 14 15:18:39 2021

Represents the various addresses types (P2PKH, P2SH, P2WPKH (SegWit))

@author: tj
"""

import hashlib
from binascii import hexlify, unhexlify

import base58check
import bech32 as bech32

from constants import NETWORK_SEGWIT_PREFIXES
from script import BTCScript


class AddressP2PKH:
    def __init__(self, address=None, hash160=None):
        if hash160:
            self.hash160 = hash160
        else:
            self.address = address;
            self.hash160 = self.internal_to_hash160()

    def to_hash160(self):
        return self.hash160

    def internal_to_hash160(self):
        addr_encoded = self.address.encode('utf-8')
        data_checksum = base58check.b58decode(addr_encoded)
        dc2 = data_checksum[1:-4]
        hexv = hexlify(dc2).decode('utf-8')
        return hexv

    def to_script_pub_key(self):
        return BTCScript(['OP_DUP', 'OP_HASH160', self.to_hash160(), 'OP_EQUALVERIFY', 'OP_CHECKSIG'])


class AddressP2SH:
    def __init__(self, script):
        self.script = script
        self.hash160 = self.to_hash160()

    def to_hash160(self):
        script_bytes = self.script.to_bytes()
        hashsha256 = hashlib.sha256(script_bytes).digest()
        hashripemd160 = hashlib.new('ripemd160')
        hashripemd160.update(hashsha256)
        hash160 = hashripemd160.digest()
        return hexlify(hash160).decode('utf-8')

    def to_p2sh_script_pub_key(self):
        return BTCScript(['OP_HASH160', self.hash160, 'OP_EQUAL'])


class AddressP2WPKH:
    def __init__(self, segwit_address=None, witness_hash=None):
        self.address = segwit_address;
        if segwit_address and not witness_hash:
            self.address_to_hash()
        else:
            self.witness_hash = witness_hash
        self.version = 0

    def to_script_pub_key(self):
        return BTCScript(['OP_0', self.to_hash()])

    def to_hash(self):
        return self.witness_hash

    def address_to_hash(self):
        witness_version, witness_int_array = bech32.decode(NETWORK_SEGWIT_PREFIXES['testnet'], self.address)
        self.witness_hash = hexlify(bytes(witness_int_array)).decode('utf-8')

    def to_string(self):
        hash_bytes = unhexlify(self.witness_hash.encode('utf-8'))
        witness_int_array = memoryview(hash_bytes).tolist()

        return bech32.encode(NETWORK_SEGWIT_PREFIXES['testnet'], self.version, witness_int_array)
