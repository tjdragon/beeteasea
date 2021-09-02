"""
Created on Mon Jun 14 15:30:10 2021

Spend coins from a AddressP2WPKH (SegWit) address to a P2PKH address
A P2PKH is of the form mfvpQsLq7T87GuUTy6fjm9XCWXjgxWGjDg
A P2WPKH is of the form tb1qdfqtkycghsdr3qgj3qc9dnev5t2zv6anef229y

@author: tj
"""

from addresses import AddressP2PKH
from key_material import KeyMaterial
from script import BTCScript
from transactions import InputTx, OutputTx, Transaction
from tx_signer import TransactionSigner

# contains the private key of the address
from_key_material = KeyMaterial(from_wif='cNDXgnmfRTbFNjD5DuFLeLZFC7qJPAR8XRYr3tWqe86r1AhmF7YY')
from_segwit_address = from_key_material.segwit_address()

# Input transaction UTXO
input_tx = InputTx('9ddebeda49427e80970c5db572a4f035e2eb64a38efc11d9575db80d2ec6d765', 0)

total_amount = 100000  # from UTXO
amount_to_send = 10000
fee = 5000

destination_address = AddressP2PKH('mzgi4XGAS75rLSPduj6otCs5ygHQX99w49')
output_tx_1 = OutputTx(amount_to_send, destination_address.to_script_pub_key())
change_address = AddressP2PKH('mfvpQsLq7T87GuUTy6fjm9XCWXjgxWGjDg')
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
