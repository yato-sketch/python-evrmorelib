# Copyright (C) 2013-2015 The python-bitcoinlib developers
#
# This file is part of python-evrmorelib.
#
# It is subject to the license terms in the LICENSE file found in the top-level
# directory of this distribution.
#
# No part of python-evrmorelib, including this file, may be copied, modified,
# propagated, or distributed except according to the terms contained in the
# LICENSE file.

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from evrmore.wallet import CEvrmoreSecret
from evrmore.signmessage import EvrmoreMessage, verifyMessage, signMessage
import sys
import os
import json

_bchr = chr
_bord = ord
if sys.version > '3':
    long = int
    def _bchr(x): return bytes([x])
    def _bord(x): return x


def load_test_vectors(name):
    with open(os.path.dirname(__file__) + '/data/' + name, 'r') as fd:
        return json.load(fd)


class Test_SignVerifyMessage(unittest.TestCase):
    def test_verify_message_simple(self):
        address = "RE34JR9zKhCLu4R7JFaDJz8JnypJDmCE14"
        message = address
        signature = "IKUeo59jk2ueeSBDkugZ9PBbteNayMn2FOKAQ1/WvoNzKcd0DeB1ljzTASm2VV8BeP//jF0aU7ztE55LIVVyOr8="

        message = EvrmoreMessage(message)

        self.assertTrue(verifyMessage(address=address, message=message, signature=signature))

    def test_verify_message_vectors(self):
        for vector in load_test_vectors('signmessage.json'):
            message = EvrmoreMessage(vector['address'])
            self.assertTrue(verifyMessage(
                address=vector['address'], message=message, signature=vector['signature']))

    def test_sign_message_simple(self):
        key = CEvrmoreSecret(
            "L1gVQSmAJDnkK1A1V3mJehL9xQbdai9CCx65d29seRFGVVheyngq")
        address = "RL5dKQv7ZZYrqSYXNVgy2HvncjcQf8G6at"
        message = address

        message = EvrmoreMessage(message)
        signature = signMessage(key, message)

        self.assertTrue(signature)
        self.assertTrue(verifyMessage(address=address, message=message, signature=signature))

    def test_sign_message_vectors(self):
        for vector in load_test_vectors('signmessage.json'):
            key = CEvrmoreSecret(vector['wif'])
            message = EvrmoreMessage(vector['address'])

            signature = signMessage(key, message)

            self.assertTrue(
                signature, "Failed to sign for [%s]" % vector['address'])
            self.assertTrue(verifyMessage(
                address=vector['address'], message=message, signature=vector['signature']), "Failed to verify signature for [%s]" % vector['address'])


if __name__ == "__main__":
    unittest.main()
