#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Aug 2nd 2021

BTC RPC

@author: tj
"""
import json

import requests

from constants import BTC_NOTE_ENDPOINT


def scantxoutset(address: str):
    data = {
        "jsonrpc": "2.0",
        "method": "scantxoutset",
        "params": ["start", ["addr(" + address + ")"]]
    }
    data_str = json.dumps(data)
    response = requests.post(BTC_NOTE_ENDPOINT, data=data_str)
    return json.loads(response.text)


def blockchaininfo():
    data = {
        "jsonrpc": "2.0",
        "method": "getblockchaininfo",
        "params": []
    }
    data_str = json.dumps(data)
    response = requests.post(BTC_NOTE_ENDPOINT, data=data_str)
    return json.loads(response.text)


def send_signed_tx(signed_tx):
    data = {
        "jsonrpc": "2.0",
        "method": "sendrawtransaction",
        "params": [signed_tx]
    }
    data_str = json.dumps(data)
    response = requests.post(BTC_NOTE_ENDPOINT, data=data_str)
    return json.loads(response.text)
