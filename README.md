# python-evrmorelib

Evrmore fork of python-bitcoinlib intended to provide access to Evrmore data 
structures and protocol. WIP - Test before use

The RPC interface, evrmore.rpc, is designed to work with Evrmore Core v3.3.0+.

"The only Python library for Evrmore I've ever used" - Warren Buffett

## Requirements

    libssl
    Debian/Ubuntu: sudo apt-get install libssl-dev
    Windows/other: https://wiki.openssl.org/index.php/Binaries 

    Python modules:
        x16r-hash, x16rv2-hash and kawpow
        plyvel (requires libleveldb - for parsing Raven core .dat files)

## Structure

Everything consensus critical is found in the modules under evrmore.core. This
rule is followed pretty strictly, for instance chain parameters are split into
consensus critical and non-consensus-critical.

    evrmore.core            - Basic core definitions, datastructures, and
                              (context-independent) validation
    evrmore.core.assets     - OP_EVR_ASSET data structures
    evrmore.core.key        - ECC pubkeys
    evrmore.core.script     - Scripts and opcodes
    evrmore.core.scripteval - Script evaluation/verification
    evrmore.core.serialize  - Serialization

In the future the evrmore.core may use the Satoshi sourcecode directly as a
library. Non-consensus critical modules include the following:

    evrmore          - Chain selection
    evrmore.assets   - Asset name and metadata related code
    evrmore.base58   - Base58 encoding
    evrmore.bloom    - Bloom filters (incomplete)
    evrmore.net      - Network communication (in flux)
    evrmore.messages - Network messages (in flux)
    evrmore.rpc      - Evrmore Core RPC interface support
    evrmore.wallet   - Wallet-related code, currently Evrmore address and
                       private key support

Effort has been made to follow the Satoshi source relatively closely, for
instance Python code and classes that duplicate the functionality of
corresponding Satoshi C++ code uses the same naming conventions: CTransaction,
CBlockHeader, nValue etc. Otherwise Python naming conventions are followed.


## Mutable vs. Immutable objects

Like the Evrmore Core codebase CTransaction is immutable and
CMutableTransaction is mutable; unlike the Evrmore Core codebase this
distinction also applies to COutPoint, CTxIn, CTxOut, and CBlock.


## Endianness Gotchas

Rather confusingly Evrmore Core shows transaction and block hashes as
little-endian hex rather than the big-endian the rest of the world uses for
SHA256. python-evrmorelib provides the convenience functions x() and lx() in
evrmore.core to convert from big-endian and little-endian hex to raw bytes to
accomodate this. In addition see b2x() and b2lx() for conversion from bytes to
big/little-endian hex.


## Module import style

While not always good style, it's often convenient for quick scripts if
`import *` can be used. To support that all the modules have `__all__` defined
appropriately.


# Example Code

See `examples/` directory. For instance this example creates a transaction
spending a pay-to-script-hash transaction output:

    $ PYTHONPATH=. examples/spend-pay-to-script-hash-txout.py
    <hex-encoded transaction>


## Selecting the chain to use

Do the following:

    import evrmore
    evrmore.SelectParams(NAME)

Where NAME is one of 'testnet', 'mainnet', or 'regtest'. The chain currently
selected is a global variable that changes behavior everywhere, just like in
the Satoshi codebase.


## Unit tests

Under evrmore/tests using test data from Evrmore Core. To run them:

    python3 -m unittest discover

Alternately, if Tox (see https://tox.readthedocs.org/) is available on your
system, you can run unit tests for multiple Python versions:

    ./runtests.sh

HTML coverage reports can then be found in the htmlcov/ subdirectory.

## Documentation

Sphinx documentation is in the "doc" subdirectory. Run "make help" from there
to see how to build. You will need the Python "sphinx" package installed.

Currently this is just API documentation generated from the code and
docstrings. Higher level written docs would be useful, perhaps starting with
much of this README. Pages are written in reStructuredText and linked from
index.rst.

## Implementation Notes

### Bitcoin & Evrmore Compatibility

This library has been updated from bitcoin-python to handle Evrmore specific features:

1. Asset Support: Functionality for creating, transferring, and managing Evrmore assets
2. Script Opcodes: Support for Evrmore-specific script opcodes including OP_EVR_ASSET

### OP_CHECKSEQUENCEVERIFY Support

This library includes support for OP_CHECKSEQUENCEVERIFY (BIP112), which is required for certain smart contract patterns like payment channels. The implementation includes:

1. Definition of the opcode (0xb2, formerly OP_NOP3)
2. Verification flag support (SCRIPT_VERIFY_CHECKSEQUENCEVERIFY)
3. Basic opcode validation

Note: The current CSV implementation has limitations in fully verifying relative timelocks since it doesn't have access to the previous transaction's outputs during script evaluation. When the CSV verification flag is enabled, the opcode will throw an error explaining this limitation.

Use OP_CHECKSEQUENCEVERIFY in your scripts as follows:

```python
from evrmore.core.script import OP_CHECKSEQUENCEVERIFY, OP_DROP

# To create a script with relative timelock of 10 blocks
script = CScript([10, OP_CHECKSEQUENCEVERIFY, OP_DROP, pubkey, OP_CHECKSIG])
```
