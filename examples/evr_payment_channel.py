#!/usr/bin/env python3
"""
Example of Payment Channel with OP_CHECKSEQUENCEVERIFY in Evrmore

This example demonstrates how to create a basic payment channel script using
OP_CHECKSEQUENCEVERIFY, which is used for relative timelocks in contracts
like the Lightning Network.

Two types of payment channel scripts are demonstrated:
1. A renewable payment channel (using CSV) - funds are locked for a relative time
2. A non-renewable payment channel (using CLTV) - funds are locked until an absolute time

Note: This example is for educational purposes only and doesn't include full
payment channel functionality like commitment transactions.
"""

import sys
if sys.version_info.major < 3:
    sys.stderr.write('Sorry, Python 3.x required by this example.\n')
    sys.exit(1)

import hashlib
from typing import Tuple

from evrmore import SelectParams
from evrmore.core import b2x, lx, COutPoint, CMutableTxOut, CMutableTxIn, CMutableTransaction, Hash160
from evrmore.core.scripteval import VerifyScript, SCRIPT_VERIFY_P2SH
from evrmore.core.script import (
    CScript, OP_DUP, OP_HASH160, OP_EQUALVERIFY, OP_CHECKSIG,
    OP_CHECKSEQUENCEVERIFY, OP_CHECKLOCKTIMEVERIFY, OP_DROP,
    OP_IF, OP_ELSE, OP_ENDIF, OP_CHECKSIG, OP_CHECKMULTISIG
)
from evrmore.wallet import P2PKHEvrmoreAddress, P2SHEvrmoreAddress, CEvrmoreSecret


def create_renewable_payment_channel(
    sender_pubkey: bytes,
    receiver_pubkey: bytes,
    blocks_timeout: int
) -> Tuple[CScript, str]:
    """
    Create a payment channel using OP_CHECKSEQUENCEVERIFY (renewable after timeout)
    
    Args:
        sender_pubkey: Sender's public key (bytes)
        receiver_pubkey: Receiver's public key (bytes)
        blocks_timeout: Number of blocks until sender can reclaim funds
    
    Returns:
        Tuple of (redeem_script, p2sh_address)
    """
    # Script format:
    # OP_IF
    #     2 <sender_pubkey> <receiver_pubkey> 2 OP_CHECKMULTISIG
    # OP_ELSE
    #     <relative_blocks> OP_CHECKSEQUENCEVERIFY OP_DROP
    #     <sender_pubkey> OP_CHECKSIG
    # OP_ENDIF
    
    redeem_script = CScript([
        OP_IF,
            2, sender_pubkey, receiver_pubkey, 2, OP_CHECKMULTISIG,
        OP_ELSE,
            blocks_timeout, OP_CHECKSEQUENCEVERIFY, OP_DROP,
            sender_pubkey, OP_CHECKSIG,
        OP_ENDIF
    ])
    
    # Get P2SH address for the redeem script
    p2sh_address = str(P2SHEvrmoreAddress.from_redeemScript(redeem_script))
    
    return redeem_script, p2sh_address


def create_nonrenewable_payment_channel(
    sender_pubkey: bytes,
    receiver_pubkey: bytes,
    absolute_block_height: int
) -> Tuple[CScript, str]:
    """
    Create a payment channel using OP_CHECKLOCKTIMEVERIFY (expires at absolute time)
    
    Args:
        sender_pubkey: Sender's public key (bytes)
        receiver_pubkey: Receiver's public key (bytes)
        absolute_block_height: Absolute block height when sender can reclaim funds
    
    Returns:
        Tuple of (redeem_script, p2sh_address)
    """
    # Script format:
    # OP_IF
    #     2 <sender_pubkey> <receiver_pubkey> 2 OP_CHECKMULTISIG
    # OP_ELSE
    #     <absolute_time> OP_CHECKLOCKTIMEVERIFY OP_DROP
    #     <sender_pubkey> OP_CHECKSIG
    # OP_ENDIF
    
    redeem_script = CScript([
        OP_IF,
            2, sender_pubkey, receiver_pubkey, 2, OP_CHECKMULTISIG,
        OP_ELSE,
            absolute_block_height, OP_CHECKLOCKTIMEVERIFY, OP_DROP,
            sender_pubkey, OP_CHECKSIG,
        OP_ENDIF
    ])
    
    # Get P2SH address for the redeem script
    p2sh_address = str(P2SHEvrmoreAddress.from_redeemScript(redeem_script))
    
    return redeem_script, p2sh_address


def explain_payment_channel_script(redeem_script: CScript) -> None:
    """Explain how a payment channel script works"""
    print("Payment Channel Script:")
    print("----------------------")
    print(f"Redeem Script (hex): {b2x(redeem_script)}")
    print(f"Script size: {len(redeem_script)} bytes")
    print("\nScript Structure:")
    print("  IF")
    print("    2 <sender_pubkey> <receiver_pubkey> 2 CHECKMULTISIG -- Cooperative close (both parties)")
    print("  ELSE")
    print("    <timeout> CHECKSEQUENCEVERIFY/CHECKLOCKTIMEVERIFY DROP -- Time-locked refund")
    print("    <sender_pubkey> CHECKSIG -- Unilateral close by sender after timeout")
    print("  ENDIF")
    print("\nThis script allows:")
    print("1. Both parties to cooperatively close the channel at any time")
    print("2. The sender to reclaim funds after the timeout if cooperation fails")


def main():
    # Use Evrmore mainnet
    SelectParams('mainnet')
    
    # Create keys for example
    # WARNING: These are example keys, never use hardcoded keys in production!
    sender_secret = CEvrmoreSecret.from_secret_bytes(hashlib.sha256(b'sender').digest())
    receiver_secret = CEvrmoreSecret.from_secret_bytes(hashlib.sha256(b'receiver').digest())
    
    sender_pubkey = sender_secret.pub
    receiver_pubkey = receiver_secret.pub
    
    print("=== Evrmore Payment Channel Example ===\n")
    print(f"Sender address: {P2PKHEvrmoreAddress.from_pubkey(sender_pubkey)}")
    print(f"Receiver address: {P2PKHEvrmoreAddress.from_pubkey(receiver_pubkey)}\n")
    
    # Create a renewable payment channel (CSV)
    csv_blocks = 144  # ~1 day of blocks
    csv_script, csv_address = create_renewable_payment_channel(
        sender_pubkey, receiver_pubkey, csv_blocks)
    
    print("RENEWABLE PAYMENT CHANNEL (using OP_CHECKSEQUENCEVERIFY)")
    print("-------------------------------------------------------")
    print(f"Channel P2SH address: {csv_address}")
    print(f"Relative timeout: {csv_blocks} blocks (~1 day)\n")
    explain_payment_channel_script(csv_script)
    
    print("\n\n")
    
    # Create a non-renewable payment channel (CLTV)
    current_block = 500000  # Example current block
    cltv_block = current_block + 1008  # ~1 week in the future
    cltv_script, cltv_address = create_nonrenewable_payment_channel(
        sender_pubkey, receiver_pubkey, cltv_block)
    
    print("NON-RENEWABLE PAYMENT CHANNEL (using OP_CHECKLOCKTIMEVERIFY)")
    print("------------------------------------------------------------")
    print(f"Channel P2SH address: {cltv_address}")
    print(f"Absolute timeout: block {cltv_block} (current block: {current_block})\n")
    explain_payment_channel_script(cltv_script)
    
    print("\n\nNote: To create a funding transaction, you would send EVR to the P2SH address.")
    print("To close the channel cooperatively, create a transaction with signatures from both parties.")
    print("For a unilateral close after timeout, create a transaction with only the sender's signature.")


if __name__ == '__main__':
    main() 