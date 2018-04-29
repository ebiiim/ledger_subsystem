Ledger Subsystem for BBc-1 (Beyond Blockchain One)
==================================================

Ledger Subsystem
----------------

**ledger_subsystem.py** contains an abstraction of BBc-1 ledger
subsystem that provides functionality for proof of existence of
transactions in a BBc-1 domain.

The following methods are provided:

-  **enable()** to enable writing to the subsystem (or initialize with
   enabled=True).
-  **disable()** to disable writing to the subsystem.
-  **set_domain(domain_id)** to set relevant domain_id.
-  **register_transaction(asset_group_id, transaction_id)** to write the
   transaction_id into a Merkle tree.
-  **verify_transaction(asset_group_id, transaction_id)** to verify that
   the transaction exists and to receive the Merkle subtree.

Ethereum Ledger Subsystem
-------------------------

**ethereum/bbc_ethereum.py** contains an abstraction of BBcAnchor smart
contract that store roots of transaction Merkle trees. It also provides
verify function that takes a Merkle subtree for verification independent
from BBc-1.

**ethereum/contracts/BBcAnchor.sol** is the solidity source code of the
BBcAnchor smart contract.

How to Use This Module
----------------------

At this stage (pre-version 1.0), we are in the process of re-organizing
the module structures as of version 0.10 of BBc-1 towards version 1.0.
When this module is ready, this README will be updated.
