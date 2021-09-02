"""
Created on August, 9th 2021

Wallet Service

@author: tj
"""

from flask import Flask, request

from kdp import KDP
from key_material import KeyMaterial
from singletons import DATABASE

app = Flask(__name__)
db = DATABASE


@app.route("/")
def ping():
    return "pong"


# curl --header "Content-Type: application/json" --request POST --data '{"account_id": "JO_LTD"}' http://127.0.0.1:5000/account/create
@app.route("/account/create", methods=['POST'])
def create_account():
    payload = request.json
    account_id = payload['account_id']
    print("Creating account id " + account_id)
    db.create_account(account_id)
    return "Account " + account_id + " created"


# {"account_id": "id", "wallet_id": "id"}
# curl --header "Content-Type: application/json" --request POST --data '{"account_id": "JO_LTD", "wallet_id": "JO_TRADING_BTC"}' http://127.0.0.1:5000/wallet/create
@app.route("/wallet/create", methods=['POST'])
def create_wallet():
    payload = request.json
    account_id = payload['account_id']
    account_index = db.get_account_index(account_id)[0][1]
    wallet_id = payload['wallet_id']
    print("Creating wallet id {} for {} @ index {}".format(wallet_id, account_id, account_index))
    for x in range(0, 10):
        # MAIN
        kdp = KDP(cointype='BTC', account=account_index, change=0, address_index=x)
        km = KeyMaterial(from_kdp=kdp)
        address = km.address()
        db.create_address(account_id, wallet_id, address, False, kdp.path())
        # CHANGE
        kdp = KDP(cointype='BTC', account=account_index, change=1, address_index=x)
        km = KeyMaterial(from_kdp=kdp)
        address = km.address()
        db.create_address(account_id, wallet_id, address, True, kdp.path())
    return "Wallet " + wallet_id + " created"


# curl --header "Content-Type: application/json" --request POST
#  --data '{"from_account_id": "JPM_UK","from_wallet_id": "JPM_BTC_0","beneficiary_address": "mg17Mdwkvw6rD7ZnhSJ9i2m4UasRzfNn6g","transfer_amount": 12345,"transfer_fee": 768}'
#  http://127.0.0.1:5000/wallet/transfer
from wallet_helper import transfer


@app.route("/wallet/transfer", methods=['POST'])
def create_transfer():
    payload = request.json
    from_account_id = payload['from_account_id']
    from_wallet_id = payload['from_wallet_id']
    beneficiary_address = payload['beneficiary_address']
    transfer_amount = payload['transfer_amount']
    transfer_fee = payload['transfer_fee']
    return transfer(from_account_id, from_wallet_id, beneficiary_address, transfer_amount, transfer_fee)


app.run()
