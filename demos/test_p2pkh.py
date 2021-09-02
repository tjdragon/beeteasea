"""
Created on Mon Jun 14 15:30:10 2021

Spend coins from a P2PKH address to a P2PKH address
A P2PKH is of the form mfvpQsLq7T87GuUTy6fjm9XCWXjgxWGjDg

@author: tj
"""

from binascii import hexlify

from addresses import AddressP2PKH
from key_material import KeyMaterial
from script import BTCScript
from transactions import InputTx, OutputTx, Transaction
from tx_signer import TransactionSigner

# BASIC TESTS
my_key_material: KeyMaterial = KeyMaterial()
my_wif_1 = my_key_material.to_wif()
my_pub_key_1 = hexlify(my_key_material.private_key_bytes)
my_adr_1 = my_key_material.address()

# ADDRESS & KEY DEFINITION
# https://www.blockchain.com/btc-testnet/address/msL7EAbrj2Bnh13bzwzLsKAjP15siQKiys
address_as_str = 'msL7EAbrj2Bnh13bzwzLsKAjP15siQKiys'
from_address = AddressP2PKH(address_as_str)
key_material = KeyMaterial(from_wif='cV7Uw6gXHJV18y1f5F3CWaCX3iUn3795HHZBWbK4BbnEhrD1TET5')

# TRANSACTION BUILDING
input_tx = InputTx('7980a37147ebc919d2e6e69c380964f98bf2fa101d5b597d528bff504d613ab2', 0)
destination_address = AddressP2PKH('mzgi4XGAS75rLSPduj6otCs5ygHQX99w49')

total_amount = 1552063  # from UTXO
amount_to_send = 500000
fee = 10000  # https://live.blockcypher.com/btc-testnet/

output_tx_1 = OutputTx(amount_to_send, BTCScript(
    ['OP_DUP', 'OP_HASH160', destination_address.to_hash160(), 'OP_EQUALVERIFY', 'OP_CHECKSIG']))
change_address = AddressP2PKH(address_as_str)
output_tx_2 = OutputTx(total_amount - amount_to_send - fee, BTCScript(
    ['OP_DUP', 'OP_HASH160', change_address.to_hash160(), 'OP_EQUALVERIFY', 'OP_CHECKSIG']))

# https://live.blockcypher.com/btc/decodetx/
my_transaction = Transaction([input_tx], [output_tx_1, output_tx_2])
my_tx_data = my_transaction.serialize()

# TRANSACTION SIGNING
transaction_signer = TransactionSigner()
unlock_script = BTCScript(['OP_DUP', 'OP_HASH160', from_address.to_hash160(), 'OP_EQUALVERIFY', 'OP_CHECKSIG'])
signed_transaction = transaction_signer.sign(my_transaction, 0, unlock_script, key_material)
print('---------------')
print('Signed Tx:')
print(signed_transaction[1])
