# python-evrmorelib release notes

## v0.2.13 - Feb 2025

* refactor of sign and verify

## v0.2.9 - Jan 2025

* made requirements file single source of truth

## v0.2.8 - Jan 2025

* included needed dependancy in requirements

## v0.2.7 - Jan 2025

* multisig (p2sh) capabilities, better vanity script

## v0.2.6 - Nov 2024

* small fixes

## v0.2.5 - Nov 2024

* fix magic string for signing messages

## v0.2.4 - Jan 2024

* set evrmore specific settings.

## v0.2.3 - Oct 2022

* Initial release as a fork from python-ravencoinlib

Python Evrmorelib is a copy of Python Ravencoinlib, based on Python bitcoinlib. It adds supports for all most important things related to Evrmore (RVN compatible coin).

0.3.0
=====

Added OP_CHECKSEQUENCEVERIFY support (BIP112):
- Implemented the opcode as OP_NOP3 (0xb2)
- Added SCRIPT_VERIFY_CHECKSEQUENCEVERIFY verification flag
- Updated script evaluation to handle CSV opcode
- Added a test case to verify the implementation
- Added an example of creating payment channels with CSV
