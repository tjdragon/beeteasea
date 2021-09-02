"""
Created on Mon Jun 14 15:24:21 2021

Represents a transaction with its inputs and outputs

@author: tj
"""

import hashlib
import struct
from binascii import hexlify, unhexlify

from script import BTCScript
from script import DEFAULT_TX_SEQUENCE

DEFAULT_TX_VERSION = b'\x02\x00\x00\x00'
DEFAULT_TX_LOCKTIME = b'\x00\x00\x00\x00'
SIGHASH_ALL = 0x01


class InputTx:
    def __init__(self, tx_id, tx_idx):
        self.tx_id = tx_id
        self.tx_idx = tx_idx
        self.script_sig = BTCScript([])
        self.sequence = DEFAULT_TX_SEQUENCE

    def stream(self):
        tx_id_bytes = unhexlify(self.tx_id)[::-1]
        tx_idx_bytes = struct.pack('<L', self.tx_idx)
        script_sig_bytes = self.script_sig.to_bytes()
        data = tx_id_bytes + tx_idx_bytes + struct.pack('B', len(script_sig_bytes)) + script_sig_bytes + self.sequence
        return data

    @classmethod
    def deep_copy(cls, tx_in):
        return cls(tx_in.tx_id, tx_in.tx_idx)


class OutputTx:
    def __init__(self, amount, unlock_script: BTCScript):
        self.amount = amount
        self.unlock_script = unlock_script

    def stream(self):
        amount_bytes = struct.pack('<q', self.amount)
        script_bytes = self.unlock_script.to_bytes()
        data = amount_bytes + struct.pack('B', len(script_bytes)) + script_bytes
        return data

    @classmethod
    def deep_copy(cls, tx_out):
        return cls(tx_out.amount, tx_out.unlock_script)


class Transaction:
    def __init__(self, inputs, outputs, with_segwit=False, witnesses=None):
        self.inputs = inputs
        self.outputs = outputs
        self.time_lock = DEFAULT_TX_LOCKTIME
        self.version = DEFAULT_TX_VERSION
        self.with_segwit = with_segwit
        if witnesses is None:
            self.witnesses = []
        else:
            self.witnesses = witnesses

    def stream(self):
        data = self.version

        if self.with_segwit and self.witnesses:
            data += b'\x00'
            data += b'\x01'

        txin_count_bytes = chr(len(self.inputs)).encode()
        txout_count_bytes = chr(len(self.outputs)).encode()
        data += txin_count_bytes
        for txin in self.inputs:
            data += txin.stream()
        data += txout_count_bytes
        for txout in self.outputs:
            data += txout.stream()

        if self.with_segwit:
            for witness in self.witnesses:
                witnesses_count_bytes = chr(len(witness.script)).encode()
                data += witnesses_count_bytes
                data += witness.to_bytes(True)

        data += self.time_lock
        return data

    def serialize(self):
        data = self.stream()
        return hexlify(data).decode('utf-8')

    @classmethod
    def deep_copy(cls, tx):
        ins = [InputTx.deep_copy(tx_in) for tx_in in tx.inputs]
        outs = [OutputTx.deep_copy(tx_out) for tx_out in tx.outputs]
        return cls(ins, outs)

    def digest(self, tx_in_index, script):
        tmp_tx = Transaction.deep_copy(self)
        for tx_in in tmp_tx.inputs:
            tx_in.script_sig = BTCScript([])
        tmp_tx.inputs[tx_in_index].script_sig = script

        tx_for_signing = tmp_tx.stream()
        tx_for_signing += struct.pack('<i', SIGHASH_ALL)
        tx_digest = hashlib.sha256(hashlib.sha256(tx_for_signing).digest()).digest()

        return tx_digest

    def segwit_digest(self, tx_in_index, script, amount):
        tmp_tx = Transaction.deep_copy(self)

        hash_prevouts = b''
        for txin in tmp_tx.inputs:
            hash_prevouts += unhexlify(txin.tx_id)[::-1] + \
                             struct.pack('<L', txin.tx_idx)
        hash_prevouts = hashlib.sha256(hashlib.sha256(hash_prevouts).digest()).digest()

        hash_sequence = b''
        for txin in tmp_tx.inputs:
            hash_sequence += txin.sequence
        hash_sequence = hashlib.sha256(hashlib.sha256(hash_sequence).digest()).digest()

        hash_outputs = b''
        for txout in tmp_tx.outputs:
            amount_bytes = struct.pack('<q', txout.amount)
            script_bytes = txout.unlock_script.to_bytes()
            hash_outputs += amount_bytes + struct.pack('B', len(script_bytes)) + script_bytes
        hash_outputs = hashlib.sha256(hashlib.sha256(hash_outputs).digest()).digest()

        tx_for_signing = self.version

        tx_for_signing += hash_prevouts + hash_sequence

        txin = self.inputs[tx_in_index]
        tx_for_signing += unhexlify(txin.tx_id)[::-1] + struct.pack('<L', txin.tx_idx)

        tx_for_signing += struct.pack('B', len(script.to_bytes()))
        tx_for_signing += script.to_bytes()

        tx_for_signing += struct.pack('<q', amount)
        tx_for_signing += txin.sequence
        tx_for_signing += hash_outputs
        tx_for_signing += self.time_lock
        tx_for_signing += struct.pack('<i', SIGHASH_ALL)

        return hashlib.sha256(hashlib.sha256(tx_for_signing).digest()).digest()
