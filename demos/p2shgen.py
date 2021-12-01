from addresses import AddressP2SH
from kdp import KDP
from key_material import KeyMaterial
from script import BTCScript

km: KeyMaterial = KeyMaterial(from_kdp=KDP('BTC', 0, 5, 0))
redeem_script = BTCScript([km.to_hex(), 'OP_CHECKSIG'])
p2sh_address = AddressP2SH(redeem_script)
p2sh_address_str = p2sh_address.to_string()