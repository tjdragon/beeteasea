"""
Created on Mon Jun 14 15:30:10 2021

Spend coins from a P2PKH address to a P2WPKH address (SegWit)
A P2PKH is of the form mfvpQsLq7T87GuUTy6fjm9XCWXjgxWGjDg
A P2WPKH is of the form tb1qdfqtkycghsdr3qgj3qc9dnev5t2zv6anef229y

@author: tj
"""

from addresses import AddressP2PKH, AddressP2WPKH
from key_material import KeyMaterial
from transactions import InputTx, OutputTx, Transaction
from tx_signer import TransactionSigner

# ADDRESS & KEY DEFINITION
# https://www.blockchain.com/btc-testnet/address/mfvpQsLq7T87GuUTy6fjm9XCWXjgxWGjDg
from_address = AddressP2PKH('mfvpQsLq7T87GuUTy6fjm9XCWXjgxWGjDg')
key_material = KeyMaterial(from_wif='cPnnc1z9XUXbvpqcijLQhPAFr4EjsaN1YosaJHkYP7b7dBwzuCnm')

# TRANSACTION BUILDING
input_tx = InputTx('d7ab7ea9a88915abc97fcebcd8e1e0d27d70658aceea43aa9761a9f3855a2a94', 1)

total_amount = 360287  # from UTXO
amount_to_send = 10000
fee = 5000

# DESTINATION
to_address = AddressP2WPKH('tb1qdfqtkycghsdr3qgj3qc9dnev5t2zv6anef229y')
output_tx_1 = OutputTx(amount_to_send, to_address.to_script_pub_key())

change_address = AddressP2PKH('mfvpQsLq7T87GuUTy6fjm9XCWXjgxWGjDg')
output_tx_2 = OutputTx(total_amount - amount_to_send - fee, change_address.to_script_pub_key())

my_transaction = Transaction([input_tx], [output_tx_1, output_tx_2])

# TRANSACTION SIGNING
transaction_signer = TransactionSigner()
signed_transaction = transaction_signer.sign(my_transaction, 0, from_address.to_script_pub_key(), key_material)
print('---------------')
print('Signed Tx:')
print(signed_transaction[1])
