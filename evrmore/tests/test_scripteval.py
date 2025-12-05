# Copyright (C) 2013-2017 The python-bitcoinlib developers
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

import json
import os
import unittest

import sys
if sys.version > '3':
    long = int

from binascii import unhexlify

from evrmore.core import *
from evrmore.core.script import *
from evrmore.core.scripteval import *


def parse_script(s):
    def ishex(s):
        return set(s).issubset(set('0123456789abcdefABCDEF'))

    r = []

    # Create an opcodes_by_name table with both OP_ prefixed names and
    # shortened ones with the OP_ dropped.
    opcodes_by_name = {}
    for name, code in OPCODES_BY_NAME.items():
        opcodes_by_name[name] = code
        opcodes_by_name[name[3:]] = code

    for word in s.split():
        if word.isdigit() or (word[0] == '-' and word[1:].isdigit()):
            r.append(CScript([long(word)]))
        elif word.startswith('0x') and ishex(word[2:]):
            # Raw ex data, inserted NOT pushed onto stack:
            r.append(unhexlify(word[2:].encode('utf8')))
        elif len(word) >= 2 and word[0] == "'" and word[-1] == "'":
            r.append(CScript([bytes(word[1:-1].encode('utf8'))]))
        elif word in opcodes_by_name:
            r.append(CScript([opcodes_by_name[word]]))
        else:
            raise ValueError("Error parsing script: %r" % s)

    return CScript(b''.join(r))


def load_test_vectors(name):
    with open(os.path.dirname(__file__) + '/data/' + name, 'r') as fd:
        for test_case in json.load(fd):
            if len(test_case) == 1:
                continue  # comment

            if len(test_case) == 3:
                test_case.append('')  # add missing comment

            scriptSig, scriptPubKey, flags, comment = test_case

            scriptSig = parse_script(scriptSig)
            scriptPubKey = parse_script(scriptPubKey)

            flag_set = set()
            for flag in flags.split(','):
                if flag == '' or flag == 'NONE':
                    pass

                else:
                    try:
                        flag = SCRIPT_VERIFY_FLAGS_BY_NAME[flag]
                    except IndexError:
                        raise Exception('Unknown script verify flag %r' % flag)

                    flag_set.add(flag)

            yield (scriptSig, scriptPubKey, flag_set, comment, test_case)


class Test_EvalScript(unittest.TestCase):
    def create_test_txs(self, scriptSig, scriptPubKey):
        txCredit = CTransaction([CTxIn(COutPoint(), CScript([OP_0, OP_0]), nSequence=0xFFFFFFFF)],
                                [CTxOut(0, scriptPubKey)],
                                nLockTime=0)
        txSpend = CTransaction([CTxIn(COutPoint(txCredit.GetTxid(), 0), scriptSig, nSequence=0xFFFFFFFF)],
                               [CTxOut(0, CScript())],
                               nLockTime=0)
        return (txCredit, txSpend)

    def test_script_valid(self):
        for scriptSig, scriptPubKey, flags, comment, test_case in load_test_vectors('script_valid.json'):
            (txCredit, txSpend) = self.create_test_txs(scriptSig, scriptPubKey)

            try:
                VerifyScript(scriptSig, scriptPubKey, txSpend, 0, flags)
            except ValidationError as err:
                self.fail('Script FAILED: %r %r %r with exception %r' %
                          (scriptSig, scriptPubKey, comment, err))

    def test_script_invalid(self):
        for scriptSig, scriptPubKey, flags, comment, test_case in load_test_vectors('script_invalid.json'):
            (txCredit, txSpend) = self.create_test_txs(scriptSig, scriptPubKey)

            try:
                VerifyScript(scriptSig, scriptPubKey, txSpend, 0, flags)
            except ValidationError:
                continue

            self.fail('Expected %r to fail' % test_case)
            
    def test_csv_implementation(self):
        """Test that our OP_CHECKSEQUENCEVERIFY implementation behaves as expected"""
        
        # Test 1: Basic detection of OP_CHECKSEQUENCEVERIFY in script
        scriptSig = CScript([])
        scriptPubKey = CScript([OP_1, OP_CHECKSEQUENCEVERIFY, OP_DROP, OP_1])
        (txCredit, txSpend) = self.create_test_txs(scriptSig, scriptPubKey)
        
        # Should pass when CSV is not enforced (treated as NOP)
        flags = set()
        VerifyScript(scriptSig, scriptPubKey, txSpend, 0, flags)
        
        # Should fail when CSV is enforced (our implementation throws EvalScriptError)
        flags = {SCRIPT_VERIFY_CHECKSEQUENCEVERIFY}
        try:
            VerifyScript(scriptSig, scriptPubKey, txSpend, 0, flags)
            self.fail('Expected CHECKSEQUENCEVERIFY to fail but it passed')
        except EvalScriptError:
            # Expected - our implementation throws because it can't fully validate CSV
            pass
        
        # Test 2: Verify that the opcode is correctly recognized
        script = CScript([OP_CHECKSEQUENCEVERIFY])
        self.assertEqual(script[0], 0xb2)
        self.assertEqual(OPCODE_NAMES[script[0]], 'OP_CHECKSEQUENCEVERIFY')
        
        # Test 3: Script parsing recognizes the opcode name
        script = parse_script('CHECKSEQUENCEVERIFY')
        self.assertEqual(script[0], 0xb2)
        
        # Test 4: Alias to OP_NOP3 works
        script = parse_script('NOP3')
        self.assertEqual(script[0], 0xb2)
        self.assertEqual(script[0], OP_CHECKSEQUENCEVERIFY)
