#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Dec, 3rd 2021

Demonstrates the perfect notional transfer (WIP)

@author: tj
"""

from addresses import AddressP2PKH, AddressP2SH
from key_material import KeyMaterial
from script import BTCScript
from transactions import InputTx, OutputTx, Transaction
from tx_signer import TransactionSigner

# address we are going to spend from
from_address = AddressP2PKH('mzgi4XGAS75rLSPduj6otCs5ygHQX99w49')
# contains the private key of the address
from_key_material = KeyMaterial(from_wif='cSiz4gDZuLXVcW1rWhJ2EZNT69LXNyVtizumQkmQEEfkACbG9oWb')

# Input transaction UTXO
input_tx_1 = InputTx('ee156d794460f6abbbadbff72413840b042b12c3899d292c2740b55b9a12e48c', 1)
input_tx_2 = InputTx('ee25841641dba335fe8d4eb62d58354301c6e28b2bc7c6802b1ef187d6662dab', 0)

# to public address - used for testing
to_key_material: KeyMaterial = KeyMaterial(from_wif='cPnnc1z9XUXbvpqcijLQhPAFr4EjsaN1YosaJHkYP7b7dBwzuCnm')
to_pub_key_hex = to_key_material.to_hex()

total_amount = 948500 + 10000  # from both UTXOs
amount_to_send = 80000
fee = 10000

redeem_script = BTCScript([to_pub_key_hex, 'OP_CHECKSIG'])
p2sh_address = AddressP2SH(redeem_script)
output_tx = OutputTx(amount_to_send, p2sh_address.to_p2sh_script_pub_key())

change_address = AddressP2PKH('mzgi4XGAS75rLSPduj6otCs5ygHQX99w49')
output_tx_2 = OutputTx(total_amount - amount_to_send - fee, BTCScript(
    ['OP_DUP', 'OP_HASH160', change_address.to_hash160(), 'OP_EQUALVERIFY', 'OP_CHECKSIG']))

trp_ref = "trp_ref".encode("utf-8").hex() # https://www.travelruleprotocol.org/
meta_tx = OutputTx(0, BTCScript(['OP_RETURN', trp_ref]))

# https://live.blockcypher.com/btc/decodetx/
my_transaction = Transaction([input_tx_1, input_tx_2], [output_tx, output_tx_2, meta_tx])
raw_unsigned_tx = my_transaction.serialize()  # All good til here

transaction_signer = TransactionSigner()

unlock_script_1 = BTCScript(['OP_DUP', 'OP_HASH160', from_address.to_hash160(), 'OP_EQUALVERIFY', 'OP_CHECKSIG'])
sig_1 = transaction_signer.sign(my_transaction, 0, unlock_script_1, from_key_material)
input_sig_1 = sig_1[0]
input_tx_1.script_sig = BTCScript([input_sig_1, from_key_material.to_hex()])

unlock_script_2 = BTCScript(['OP_DUP', 'OP_HASH160', from_address.to_hash160(), 'OP_EQUALVERIFY', 'OP_CHECKSIG'])
sig_2 = transaction_signer.sign(my_transaction, 1, unlock_script_2, from_key_material)
input_sig_2 = sig_2[0]
input_tx_2.script_sig = BTCScript([input_sig_2, from_key_material.to_hex()])

signed_tx = my_transaction.serialize()

print('-- https://live.blockcypher.com/btc/decodetx/')
print('Signed Tx:')
print(signed_tx)
