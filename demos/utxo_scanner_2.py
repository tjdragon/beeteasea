"""
Created on Friday, August 6th 2021

UTXO Scanner

@author: tj
"""
import json

from btc_rpc import scantxoutset
from constants import ONE_BTC
from singletons import DATABASE

print("***** UTXO SCANNER V2 *****")

db_instance = DATABASE
while True:
    coin_data = db_instance.select_coin_data()
    for coin in coin_data:
        # print("Retrieved address " + str(coin_data))
        account_id = coin[0]
        wallet_id = coin[1]
        address = coin[2]
        print("Scanning " + address)
        utxos = scantxoutset(address)
        success = utxos["result"]["success"]
        print("Success..." + str(success))
        if success:
            ta = utxos["result"]["total_amount"]
            total_amount = int(ta * ONE_BTC)
            db_instance.insert_coin_data(
                account_id,
                wallet_id,
                address,
                total_amount,
                json.dumps(utxos))
