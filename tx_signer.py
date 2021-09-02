"""
Created on Mon Jun 14 15:26:37 2021

The transaction signer code. Fairly complex due to:
  https://github.com/bitcoin/bips/blob/master/bip-0062.mediawiki#low-s-values-in-signatures

@author: tj
"""

import hashlib
import struct
from binascii import hexlify, unhexlify

from ecdsa.util import sigencode_der

from key_material import KeyMaterial
from script import BTCScript
from transactions import SIGHASH_ALL
from transactions import Transaction


class TransactionSigner:
    def __init__(self):
        print('Transaction Signer')

    def internal_sign(self, tx: Transaction, tx_index: int, key_material: KeyMaterial, tx_digest: bytes):
        signature = key_material.private_key.sign_digest_deterministic(
            tx_digest,
            sigencode=sigencode_der,
            hashfunc=hashlib.sha256)

        # https://github.com/bitcoin/bips/blob/master/bip-0062.mediawiki#low-s-values-in-signatures
        der_prefix = signature[0]
        length_total = signature[1]
        der_type_int = signature[2]
        length_r = signature[3]
        R = signature[4:4 + length_r]
        length_s = signature[5 + length_r]
        S = signature[5 + length_r + 1:]
        S_as_bigint = int(hexlify(S).decode('utf-8'), 16)

        _order = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
        half_order = _order // 2
        if S_as_bigint > half_order:
            assert length_s == 0x21
            new_S_as_bigint = _order - S_as_bigint
            new_S = unhexlify(format(new_S_as_bigint, 'x').zfill(64))
            assert len(new_S) == 0x20
            length_s -= 1
            length_total -= 1
        else:
            new_S = S

        # reconstruct signature
        signature = struct.pack('BBBB', der_prefix, length_total, der_type_int, length_r) + R + \
                    struct.pack('BB', der_type_int, length_s) + new_S

        signature += struct.pack('B', SIGHASH_ALL)

        signature_hex = hexlify(signature).decode('utf-8')
        public_key_hex = key_material.to_hex()
        tx.inputs[tx_index].script_sig = BTCScript([signature_hex, public_key_hex])
        signed_tx = tx.serialize()

        return (signature_hex, signed_tx)

    def sign(self, tx: Transaction, tx_index: int, unlock_script: BTCScript, key_material: KeyMaterial):
        tx_digest = tx.digest(tx_index, unlock_script)
        return self.internal_sign(tx, tx_index, key_material, tx_digest)

    def sign_segwit(self, tx: Transaction, tx_index: int, unlock_script: BTCScript, key_material: KeyMaterial, amount):
        tx_digest = tx.segwit_digest(tx_index, unlock_script, amount)
        return self.internal_sign(tx, tx_index, key_material, tx_digest)
