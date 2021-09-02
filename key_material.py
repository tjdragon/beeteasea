"""
Created on Mon Jun 14 15:20:10 2021

@author: tj
"""

import hashlib
from binascii import hexlify, unhexlify

import base58check
from bip32 import BIP32
from ecdsa import SigningKey, VerifyingKey, SECP256k1

from addresses import AddressP2WPKH, AddressP2PKH
from constants import TEST_PRIVATE_KEY, PRIVATE_KEY_COMPRESSED_PUBKEY, TEST_PUBKEY_HASH, MASTERSEED
from kdp import KDP


class KeyMaterial:
    def __init__(self, from_wif=None, from_kdp: KDP = None):
        if from_kdp is not None:
            bip32 = BIP32.from_seed(bytes.fromhex(MASTERSEED))
            priv_bytes = bip32.get_privkey_from_path(from_kdp.path())
            self.private_key: SigningKey = SigningKey.from_string(priv_bytes, curve=SECP256k1)
            self.private_key_bytes = self.private_key.to_string()
            self.public_key: VerifyingKey = self.private_key.get_verifying_key()
            self.public_key_bytes = self.public_key.to_string()
            self.compressed = True
        elif from_wif is not None:
            wif_utf = from_wif.encode('utf-8')
            data_bytes = base58check.b58decode(wif_utf)
            key_bytes = data_bytes[:-4]
            checksum = data_bytes[-4:]
            data_hash = hashlib.sha256(hashlib.sha256(key_bytes).digest()).digest()
            if not checksum == data_hash[0:4]:
                raise ValueError('Checksum error!')
            network_prefix = key_bytes[:1]
            if TEST_PRIVATE_KEY != network_prefix:
                raise ValueError('Should be test network')
            key_bytes = key_bytes[1:]
            if len(key_bytes) > 32:
                self.private_key = SigningKey.from_string(key_bytes[:-1], curve=SECP256k1)
            else:
                self.private_key = SigningKey.from_string(key_bytes, curve=SECP256k1)
            self.private_key_bytes = self.private_key.to_string()
            self.public_key: VerifyingKey = self.private_key.get_verifying_key()
            self.public_key_bytes = self.public_key.to_string()
            self.compressed = True
        else:
            self.private_key: SigningKey = SigningKey.generate(curve=SECP256k1)
            self.private_key_bytes = self.private_key.to_string()
            self.public_key: VerifyingKey = self.private_key.get_verifying_key()
            self.public_key_bytes = self.public_key.to_string()
            self.compressed = True

    def to_wif(self) -> str:
        prefix = TEST_PRIVATE_KEY
        suffix = PRIVATE_KEY_COMPRESSED_PUBKEY  # Because compressed
        key_data = prefix + self.private_key_bytes + suffix
        data_hash = hashlib.sha256(hashlib.sha256(key_data).digest()).digest()
        checksum = data_hash[0:4]
        wif = base58check.b58encode(key_data + checksum)
        return wif.decode('utf-8')

    def to_hex(self, compressed=True):
        key_hex = hexlify(self.public_key.to_string())

        if compressed:
            if int(key_hex[-2:], 16) % 2 == 0:
                key_str = b'02' + key_hex[:64]
            else:
                key_str = b'03' + key_hex[:64]
        else:
            key_str = b'04' + key_hex  # Uncompressed starts with 04

        return key_str.decode('utf-8')

    def to_hash160(self, compressed=True):
        pubkey = unhexlify(self.to_hex(compressed))
        hashsha256 = hashlib.sha256(pubkey).digest()
        hashripemd160 = hashlib.new('ripemd160')
        hashripemd160.update(hashsha256)
        hash160 = hashripemd160.digest()
        return hash160

    def address(self):
        hash160 = self.to_hash160(True)
        # addr_string_hex = hexlify(hash160).decode('utf-8')
        # print('addr_string_hex', addr_string_hex)
        data = TEST_PUBKEY_HASH + hash160
        data_hash = hashlib.sha256(hashlib.sha256(data).digest()).digest()
        checksum = data_hash[0:4]
        address_bytes = base58check.b58encode(data + checksum)
        return address_bytes.decode('utf-8')

    def segwit_address(self):
        hash160 = self.to_hash160()
        addr_string_hex = hexlify(hash160).decode('utf-8')
        return AddressP2WPKH(witness_hash=addr_string_hex)

    def p2pkh(self):
        hash160 = self.to_hash160(True)
        addr_string_hex = hexlify(hash160).decode('utf-8')
        return AddressP2PKH(hash160=addr_string_hex)

# km  = KeyMaterial()
# wif = km.to_wif()
# adr = km.address()
