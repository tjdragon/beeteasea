#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Mon Jun 14 16:09:04 2021

Simple coin selector which selects the transactions by oldest first then amount

@author: tj
"""
import btc_rpc
from constants import ONE_BTC
from singletons import DATABASE


class Coin:
    def __init__(self, address, kdp, height, tx_id, vout, amount):
        self.address = address
        self.kdp = kdp
        self.height = height
        self.tx_id = tx_id
        self.vout = vout
        self.amount = amount

    def __getitem__(self, key):
        return getattr(self, key)

    @classmethod
    def to_coin(cls, dict):
        return Coin(dict['address'], dict['kdp'], dict['height'], dict['tx_id'], dict['vout'], dict['amount'])

    def __str__(self):
        return self.address + "/" + self.tx_id + "/" + self.amount


class CoinSelector:
    def __init__(self, account_id, wallet_id):
        self.account_id = account_id
        self.wallet_id = wallet_id
        self.best_block = -1
        self.coins = []
        self.init()
        print(str(self.coins))

    def init(self):
        bi = btc_rpc.blockchaininfo()
        self.best_block = bi['result']['blocks']

        coin_data = DATABASE.select_coin_data(self.account_id, self.wallet_id)
        for coin in coin_data:
            address = coin[2]
            kdp = coin[6]
            utxos = coin[8]
            unspents = utxos['result']['unspents']
            for unspent in unspents:
                height = unspent['height']
                tx_id = unspent['txid']
                vout = unspent['vout']
                amount = int(unspent['amount'] * ONE_BTC)
                self.coins.append(Coin(address, kdp, height, tx_id, vout, amount))

    def select(self, amount_to_send, fee):
        selected_coins = []
        sorted_coins = self.sort_coins()

        current_amount = 0
        for selected_coin in sorted_coins:
            current_amount = current_amount + selected_coin["amount"]
            selected_coins.append(selected_coin)
            if current_amount >= (amount_to_send + fee):
                break

        if current_amount < amount_to_send + fee:
            selected_coins = []

        return [Coin.to_coin(e) for e in selected_coins]

    def sort_coins(self):
        coins_dict = [c.__dict__ for c in self.coins]
        sorted_coins = sorted(coins_dict, key=lambda k: (self.best_block - k["height"], k["amount"]))
        return sorted_coins
