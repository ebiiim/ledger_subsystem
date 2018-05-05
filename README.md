Ledger Subsystem for BBc-1 (Beyond Blockchain One)
===========================================
## Ledger Subsystem
**bbc1/core/ledger_subsystem.py** provides functionality for proof of existence of transactions in a BBc-1 domain, using existing blockchains. This functionality is intended for use prior to expansion of the BBc-1 inter-domain network and widespread use of intercrossing references for proof of existence.

The following methods are provided:

* **enable()** to enable writing to the subsystem (or initialize with enabled=True).
* **disable()** to disable writing to the subsystem.
* **register_transaction(transaction_id)** to write the transaction_id into a Merkle tree.
* **verify_transaction(transaction_id)** to verify that the transaction exists and to receive the Merkle subtree.

## Ledger Subsystem with Ethereum
**bbc1/core/ethereum/bbc_ethereum.py** contains an abstraction of BBcAnchor smart contract that store roots of transaction Merkle trees. It also provides verify function that takes a Merkle subtree for verification independent from BBc-1.

**bbc1/core/ethereum/contracts/BBcAnchor.sol** is the solidity source code of the BBcAnchor smart contract.

## Subsystem Tools
**bbc1/core/subsystem_tool_lib.py** contains the base class definition for creating a subsystem tool.

**utils/eth_subsytem_tool.py** is the subsystem tool for the ledger subsystem with Ethereum. See README at **bbc1/core/ethereum** for detail instruction.

## How to Use This Module
At this stage (pre-version 1.0), we are in the process of re-organizing the module structures as of version 0.10 of BBc-1 towards version 1.0. When this module is ready, this README will be updated.
