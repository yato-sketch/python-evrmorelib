# using entropy to generate a private key and address
# >>> import os
# >>> import mnemonic
# >>> from evrmore.wallet import P2PKHEvrmoreAddress, CEvrmoreSecret
# >>> evrmore.SelectParams('mainnet')
# >>> entropy = os.urandom(32)
# >>> entropy.hex()
# '4ad5e01ffe06582456ea39b807bf834b16f6a696c9eec424eb6595c0c80ba04b'
# >>> mnemonic.Mnemonic('english').to_mnemonic(entropy)
# 'enlist pyramid among winter grain banana forum elbow retreat digital this normal hunt fashion forest differ service chef sunny clog arrive alarm license immune'
# >>> mnemonic.Mnemonic('english').to_mnemonic(entropy[:16])
# 'enlist pyramid among winter grain banana forum elbow retreat digital this nurse'
# >>> entropy
# b'J\xd5\xe0\x1f\xfe\x06X$V\xea9\xb8\x07\xbf\x83K\x16\xf6\xa6\x96\xc9\xee\xc4$\xebe\x95\xc0\xc8\x0b\xa0K'
# >>> entropy.hex()
# '4ad5e01ffe06582456ea39b807bf834b16f6a696c9eec424eb6595c0c80ba04b'
# >>> priv = CEvrmoreSecret.from_secret_bytes(entropy)
# >>> addr = P2PKHEvrmoreAddress.from_pubkey(priv.pub)
# >>> priv.pub.hex()
# '0234b13fc1280727921db0892c034213f5b8d53dd3eb2ff54d78ce50872da24f10'
# >>> priv.hex()
# '4ad5e01ffe06582456ea39b807bf834b16f6a696c9eec424eb6595c0c80ba04b01'
# >>> addr.hex()
# 'a75684190f8adc0597aee2d707f4811a57f6ac81'
# >>> str(priv)
# 'KyjBTshKFhBHUo13iw5rwH4orSyczYxo5HJxXa2Nrxs9ujNbHq4f'
#
# generating script hash from address
# >>> from base58 import b58decode_check
# >>> from binascii import hexlify
# >>> from hashlib import sha256
# >>> import codecs
# >>> OP_DUP = b'76'
# >>> OP_HASH160 = b'a9'
# >>> BYTES_TO_PUSH = b'14'
# >>> OP_EQUALVERIFY = b'88'
# >>> OP_CHECKSIG = b'ac'
# >>> def DATA_TO_PUSH(address): return hexlify(b58decode_check(address)[1:])
# ...
# >>> def sig_script_raw(address): return b''.join(
# ...             (OP_DUP, OP_HASH160, BYTES_TO_PUSH, DATA_TO_PUSH(address), OP_EQUALVERIFY, OP_CHECKSIG))
# ...
# >>> def scripthash(address): return sha256(codecs.decode(
# ...             sig_script_raw(address), 'hex_codec')).digest()[::-1].hex()
# ...
# >>> scripthash(str(addr))
# '1f96edabacf92b197f4036af00256b2dc952e09d1b4935f07c5386333ffd764b'
#
# testing signing and verifying a message with the private key
# >>> from typing import Union
# >>> from evrmore.signmessage import EvrmoreMessage, signMessage
# >>> def signMessage(key: CEvrmoreSecret, message: Union[str, EvrmoreMessage]):
# ...     ''' returns binary signature '''
# ...     return signMessage(
# ...         key,
# ...         EvrmoreMessage(message) if isinstance(message, str) else message)
# ...
# >>> from evrmore.signmessage import verifyMessage
# >>> def verify(
# ...     message: Union[str, EvrmoreMessage],
# ...     signature: Union[bytes, str],
# ...     publicKey: str = None,
# ...     address: str = None
# ... ):
# ...     ''' returns bool success '''
# ...     return verifyMessage(
# ...         address or generateAddress(publicKey),
# ...         EvrmoreMessage(message) if isinstance(message, str) else message,
# ...         signature if isinstance(signature, bytes) else signature.encode())
# ...
# >>> signed = signMessage(priv, EvrmoreMessage('helloworld'))
# >>> signed
# b'IJuynEWwEHOK/8CGWWc7jGGhFRfvJ0NjOk3bQk+Xqn3Ue0Xt0ejSoECmpo+SbcfMGqG+i58ij8B0mH0qifdd3/Q='
# >>> verify('helloworld', signed, address=str(addr))
# True
# >>> verify('hellowo1rld', signed, address=str(addr))
# False
