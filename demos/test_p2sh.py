#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Mon Jun 14 16:09:04 2021

Spend coins to a P2SH address
A P2PKH is of the form mfvpQsLq7T87GuUTy6fjm9XCWXjgxWGjDg

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
input_tx = InputTx('6a3659545bc33f15e89fe958b0d229d49f237c7174a6d5ffd6bb24eec699eaae', 1)

# to public address - used for testing
# kdp_0 = KDP(cointype='BTC', account=2, change=0, address_index=0)
# to_key_material = KeyMaterial(from_kdp=kdp_0)
to_key_material: KeyMaterial = KeyMaterial(from_wif='cPnnc1z9XUXbvpqcijLQhPAFr4EjsaN1YosaJHkYP7b7dBwzuCnm')
to_pub_key_hex = to_key_material.to_hex()

total_amount = 9755000  # from UTXO
fee = 10000
amount_to_send = total_amount - fee

redeem_script = BTCScript([to_pub_key_hex, 'OP_CHECKSIG'])
p2sh_address = AddressP2SH(redeem_script)
output_tx = OutputTx(amount_to_send, p2sh_address.to_p2sh_script_pub_key())

change_address = AddressP2PKH('mzgi4XGAS75rLSPduj6otCs5ygHQX99w49')
output_tx_2 = OutputTx(total_amount - amount_to_send - fee, BTCScript(
    ['OP_DUP', 'OP_HASH160', change_address.to_hash160(), 'OP_EQUALVERIFY', 'OP_CHECKSIG']))

# https://live.blockcypher.com/btc/decodetx/
my_transaction = Transaction([input_tx], [output_tx, output_tx_2])
raw_unsigned_tx = my_transaction.serialize()  # All good til here

transaction_signer = TransactionSigner()
unlock_script = BTCScript(['OP_DUP', 'OP_HASH160', from_address.to_hash160(), 'OP_EQUALVERIFY', 'OP_CHECKSIG'])
sig = transaction_signer.sign(my_transaction, 0, unlock_script, from_key_material)
input_sig = sig[0]
print("input_sig: " + input_sig)

input_tx.script_sig = BTCScript([input_sig, from_key_material.to_hex()])
signed_tx = my_transaction.serialize()

print('-- https://live.blockcypher.com/btc/decodetx/')
print('Signed Tx:')
print(signed_tx)
