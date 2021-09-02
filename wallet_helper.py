from addresses import AddressP2SH, AddressP2PKH
from btc_rpc import send_signed_tx
from coin_selector import CoinSelector, Coin
from kdp import KDP
from key_material import KeyMaterial
from script import BTCScript
from singletons import DATABASE
from transactions import OutputTx, InputTx, Transaction
from tx_signer import TransactionSigner

db = DATABASE


def transfer(from_account_id, from_wallet_id, beneficiary_address, transfer_amount, transfer_fee) -> str:
    print(
        "Sending {} (fee of {}) from {}/{} to {}".format(transfer_amount, transfer_fee, from_account_id, from_wallet_id,
                                                         beneficiary_address))

    # Where to send the coins to
    # AFAIRE: from beneficiary_address to Key : https://github.com/karask/python-bitcoin-utils/blob/e681016aae0130c2f5420a4b700bf6447b205f60/bitcoinutils/keys.py#L974
    to_key_material: KeyMaterial = KeyMaterial(from_wif='cPnnc1z9XUXbvpqcijLQhPAFr4EjsaN1YosaJHkYP7b7dBwzuCnm')
    to_pub_key_hex = to_key_material.to_hex()
    redeem_script = BTCScript([to_pub_key_hex, 'OP_CHECKSIG'])
    p2sh_address = AddressP2SH(redeem_script)
    output_tx = OutputTx(transfer_amount, p2sh_address.to_p2sh_script_pub_key())

    coin_selector = CoinSelector(from_account_id, from_wallet_id)
    selected_utxos = coin_selector.select(amount_to_send=transfer_amount, fee=transfer_fee)
    print("selected_utxos: {}".format(selected_utxos))

    keys_material_map = {}
    for selected_coin in selected_utxos:
        kdp = KDP(key_path=selected_coin.kdp)
        key_material = KeyMaterial(from_kdp=kdp)
        address_str = key_material.address()
        keys_material_map[address_str] = key_material

    change_address = db.get_address(from_account_id, from_wallet_id, True)
    change_kdp = KDP(key_path=change_address[0][6])
    change_key_material = KeyMaterial(from_kdp=change_kdp)
    change_address_str = change_key_material.address()
    keys_material_map[change_address_str] = change_key_material

    # And the change to
    total_amount = sum(u.amount for u in selected_utxos)
    change_address = AddressP2PKH(change_address_str)
    change_amount = total_amount - transfer_amount - transfer_fee
    output_tx_2 = OutputTx(change_amount, BTCScript(
        ['OP_DUP', 'OP_HASH160', change_address.to_hash160(), 'OP_EQUALVERIFY', 'OP_CHECKSIG']))

    # Create the list of input transactions
    def utxo_to_input(utxo: Coin) -> InputTx:
        return InputTx(utxo.tx_id, utxo.vout)

    inputs = list(map(utxo_to_input, selected_utxos))

    trp_ref = "trp_ref_123".encode("utf-8").hex()
    meta_tx = OutputTx(0, BTCScript(['OP_RETURN', trp_ref]))

    my_transaction = Transaction(inputs, [output_tx, output_tx_2, meta_tx])

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
    print('Signed Tx: {}'.format(signed_tx))

    result = send_signed_tx(signed_tx)

    return str(
        result)  # https://www.blockchain.com/btc-testnet/tx/5d46985a7c7335e7e187e46730cb7794de49210773abf3c05d501350db946075

# output = transfer('JPM_UK', 'JPM_BTC_0', 'mg17Mdwkvw6rD7ZnhSJ9i2m4UasRzfNn6g', 12345, 678)
# print("Result: {}".format(output))
