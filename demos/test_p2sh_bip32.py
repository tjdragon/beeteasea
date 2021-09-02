#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Mon Jun 14 16:09:04 2021

Spend coins to a P2SH address
A P2PKH is of the form mfvpQsLq7T87GuUTy6fjm9XCWXjgxWGjDg

This code uses BIP32 to manage addresses and key derivation

@author: tj
"""
import sys

from addresses import AddressP2PKH, AddressP2SH
from btc_rpc import send_signed_tx
from coin_selector import Coin, CoinSelector
from kdp import KDP
from key_material import KeyMaterial
from script import BTCScript
from transactions import InputTx, OutputTx, Transaction
from tx_signer import TransactionSigner

ACCOUNT_ID = 'JPM_UK'
WALLET_ID = 'JPM_BTC_0'
DEFAULT_ACCOUNT = 2

kdp_0 = KDP(cointype='BTC', account=DEFAULT_ACCOUNT, change=0, address_index=0)
from_key_material = KeyMaterial(from_kdp=kdp_0)
address_str = from_key_material.address()
print("address_str: " + address_str)  # 'mnqnsMe6p71sejEa2UJMCd9Z6wU4NKLpD6'

kdp_1 = KDP(cointype='BTC', account=DEFAULT_ACCOUNT, change=1, address_index=0)
change_key_material = KeyMaterial(from_kdp=kdp_1)
change_address_str = change_key_material.address()
print("change_address_str: " + change_address_str)  # 'mg17Mdwkvw6rD7ZnhSJ9i2m4UasRzfNn6g'

keys_material_map = {address_str: from_key_material, change_address_str: change_key_material}

# This is the amount we would like to send
amount_to_send = 20000
fee = 40000

coin_selector = CoinSelector(ACCOUNT_ID, WALLET_ID)
selected_utxos = coin_selector.select(amount_to_send=amount_to_send, fee=fee)
print("selected_utxos: " + str(selected_utxos))

# Where to send the coins to
to_key_material: KeyMaterial = KeyMaterial(from_wif='cPnnc1z9XUXbvpqcijLQhPAFr4EjsaN1YosaJHkYP7b7dBwzuCnm')
to_pub_key_hex = to_key_material.to_hex()
redeem_script = BTCScript([to_pub_key_hex, 'OP_CHECKSIG'])
p2sh_address = AddressP2SH(redeem_script)
output_tx = OutputTx(amount_to_send, p2sh_address.to_p2sh_script_pub_key())

# And the change to
total_amount = sum(u.amount for u in selected_utxos)
change_address = AddressP2PKH(change_address_str)
change_amount = total_amount - amount_to_send - fee
output_tx_2 = OutputTx(change_amount, BTCScript(
    ['OP_DUP', 'OP_HASH160', change_address.to_hash160(), 'OP_EQUALVERIFY', 'OP_CHECKSIG']))


# Create the list of input transactions
def utxo_to_input(utxo: Coin) -> InputTx:
    return InputTx(utxo.tx_id, utxo.vout)


inputs = list(map(utxo_to_input, selected_utxos))

# https://live.blockcypher.com/btc/decodetx/
my_transaction = Transaction(inputs, [output_tx, output_tx_2])
raw_unsigned_tx = my_transaction.serialize()  # All good til here

# Sign the transaction
transaction_signer = TransactionSigner()
tx_index = 0
for utxo in selected_utxos:
    utxo_address = utxo.address
    unlock_script = BTCScript(
        ['OP_DUP', 'OP_HASH160', AddressP2PKH(utxo_address).to_hash160(), 'OP_EQUALVERIFY', 'OP_CHECKSIG'])
    key_material = keys_material_map[utxo_address]
    sig = transaction_signer.sign(my_transaction, tx_index, unlock_script, key_material)
    input_sig = sig[0]
    inputs[tx_index].script_sig = BTCScript([input_sig, key_material.to_hex()])
    tx_index = tx_index + 1

signed_tx = my_transaction.serialize()

# https://live.blockcypher.com/btc-testnet/tx/09c1c8d449dcc15e039bfa4b42678fb8e85cd0e830846b94ee154c2c948ee34e/
print('-- https://live.blockcypher.com/btc/decodetx/')
print('Signed Tx:')
print(signed_tx)

result = send_signed_tx(signed_tx)
print('Result' + str(result))

sys.exit()
