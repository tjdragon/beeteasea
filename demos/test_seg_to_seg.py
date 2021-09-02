#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Mon Jun 14 16:09:04 2021

Spend coins from a P2WPKH address (SegWit) to a P2WPKH address (SegWit)
A P2WPKH is of the form tb1qdfqtkycghsdr3qgj3qc9dnev5t2zv6anef229y

@author: tj
"""

from addresses import AddressP2WPKH
from key_material import KeyMaterial
from script import BTCScript
from transactions import InputTx, OutputTx, Transaction
from tx_signer import TransactionSigner

# contains the private key of the address
from_key_material = KeyMaterial(from_wif='cNDXgnmfRTbFNjD5DuFLeLZFC7qJPAR8XRYr3tWqe86r1AhmF7YY')

# Input transaction UTXO
input_tx = InputTx('d2c897cdc9494791b34622671c3a8ded2d6b32a6e5e0d57562385b7839c15406', 0)

total_amount = 10000  # from UTXO
amount_to_send = 5000
fee = 1000

# DESTINATION
to_key_material = KeyMaterial()
to_segwit_address = to_key_material.segwit_address()
to_segwit_address_str = to_segwit_address.to_string()
to_address = AddressP2WPKH(to_segwit_address_str)
output_tx_1 = OutputTx(amount_to_send, to_address.to_script_pub_key())

change_address = AddressP2WPKH('tb1qdfqtkycghsdr3qgj3qc9dnev5t2zv6anef229y')
output_tx_2 = OutputTx(total_amount - amount_to_send - fee, change_address.to_script_pub_key())

my_transaction = Transaction([input_tx], [output_tx_1, output_tx_2], with_segwit=True)

script_code = from_key_material.p2pkh().to_script_pub_key()

transaction_signer = TransactionSigner()
sig = transaction_signer.sign_segwit(my_transaction, 0, script_code, from_key_material, total_amount)
segwit_signature = sig[0]

input_tx.script_sig = BTCScript([])  # Otherwise Witness requires empty scriptSig
my_transaction.witnesses.append(BTCScript([segwit_signature, from_key_material.to_hex()]))

signed_tx = my_transaction.serialize()

print('-- https://live.blockcypher.com/btc/decodetx/')
print('Signed Tx:')
print(signed_tx)
