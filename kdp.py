"""
Created on July 28th 2021

https://github.com/satoshilabs/slips/blob/master/slip-0044.md
https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki
https://wiki.trezor.io/BIP44#BIP44

Change
Constant 0 is used for external chain and constant 1 for internal chain (also known as change addresses). External chain is used for addresses that are meant to be visible outside of the wallet (e.g. for receiving payments). Internal chain is used for addresses which are not meant to be visible outside of the wallet and is used for return transaction change.

Public derivation is used at this level.

Index
Addresses are numbered from index 0 in sequentially increasing manner. This number is used as child index in BIP32 derivation.

Public derivation is used at this level.

m / 44' / coin_type' / account' / change / address

@author: tj
"""

COIN_TYPE = {'BTC': '0',
             'TESTNET': '1',
             'LTC': '2',
             'ETH': '60'}


class KDP:

    def __init__(self,
                 cointype: str = None,
                 account: int = None,
                 change: int = None,
                 address_index: int = None,
                 key_path: str = None):
        if key_path is None:
            self.kdp = "m/44'/{}'/{}'/{}/{}".format(COIN_TYPE[cointype], account, change, address_index)
        else:
            self.kdp = key_path

    def path(self) -> str:
        return self.kdp
