"""
Created on Mon Jun 14 15:20:10 2021

Constants used everywhere

@author: tj
"""

BTC_NOTE_ENDPOINT = "http://localhost:8332/"
ONE_BTC = 100000000
MASTERSEED = "TJ's Super Master Seed".encode('utf-8').hex()
TEST_PRIVATE_KEY = b'\xef'
TEST_PUBKEY_HASH = b'\x6f'
PRIVATE_KEY_COMPRESSED_PUBKEY = b'\x01'
NETWORK_SEGWIT_PREFIXES = {'mainnet': 'bc',
                           'testnet': 'tb',
                           'regtest': 'bcrt'}
