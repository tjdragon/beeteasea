"""
Created on July 29

@author: tj
"""
import hashlib

from bip32 import BIP32
# Simulate HSM initialisation
from ecdsa import SigningKey, SECP256k1, VerifyingKey
from key_material import KeyMaterial

from kdp import KDP

MASTERSEED = "RANDOM_SEED_TBD".encode('utf-8').hex()
bip32 = BIP32.from_seed(bytes.fromhex(MASTERSEED))

# Domain (Root or otherwise) - 2 sample wallets
wallet_1_kdp = "m/1'/1'"
wallet_1_xpriv = bip32.get_xpriv_from_path(wallet_1_kdp)

# Generate an address for a given wallet id & kdp
wallet_1_kdp_1 = KDP(key_path=wallet_1_kdp)
wallet_1_kdp_1_key_material = KeyMaterial(from_kdp=wallet_1_kdp_1)
wallet_1_kdp_1_address = wallet_1_kdp_1_key_material.address()  # 'n2GFmgVR6gygj6dRtQxFYQx2jfXKomyF61'

# Sign the address wit the private key
# First generate a signing key from the private key
wallet_1_xpriv_bytes = bip32.get_privkey_from_path(wallet_1_kdp)
wallet_1_signing_key = SigningKey.from_string(wallet_1_xpriv_bytes, curve=SECP256k1)

# Sign the address with the private key and generate a signature
wallet_1_kdp_1_address_bytes = wallet_1_kdp_1_address.encode('utf-8')
wallet_1_signature_bytes = wallet_1_signing_key.sign(
    wallet_1_kdp_1_address_bytes,
    hashfunc=hashlib.sha256)
wallet_1_signature_hex = wallet_1_signature_bytes.hex()

# Verify the signature by using the public key
# First generate the verifying key from the same key path
wallet_1_xpub_bytes = bip32.get_pubkey_from_path(wallet_1_kdp)
wallet_1_xpub = bip32.get_xpub_from_path(wallet_1_kdp)
wallet_1_veryfing_key = VerifyingKey.from_string(wallet_1_xpub_bytes, curve=SECP256k1)
wallet_1_verified = wallet_1_veryfing_key.verify(wallet_1_signature_bytes,
                                                 wallet_1_kdp_1_address_bytes,
                                                 hashfunc=hashlib.sha256)
assert wallet_1_verified

# This is the first address we would generate to receive theoretically
wallet_1_kdp_pub = "m/1'/1'/0"
wallet_1_kdp_pub_key_material = KeyMaterial(from_kdp=KDP(key_path=wallet_1_kdp_pub))
wallet_1_kdp_pub_address = wallet_1_kdp_pub_key_material.address()  # 'msCTSHVEADiYLubiCt1eWc7gLhq8trTA5k'
