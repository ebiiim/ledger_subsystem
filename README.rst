Ledger Subsystem for BBc-1 (Beyond Blockchain One)
==================================================

Ledger Subsystem
----------------

**bbc1/core/ledger_subsystem.py** provides functionality for proof of
existence of transactions in BBc-1 domains, using existing blockchains.
This functionality is intended for use prior to expansion of the BBc-1
inter-domain network and widespread use of intercrossing references
(Proof of Context) for proof of existence.

The following methods are provided:

-  **enable()** to enable writing to the subsystem (or initialize with
   enabled=True).
-  **disable()** to disable writing to the subsystem.
-  **register_transaction(transaction_id)** to write the digest (not
   necessarily transaction_id) into a Merkle tree.
-  **verify_transaction(transaction_id)** to verify that the digest (not
   necessarily of transaction) exists and to receive the Merkle subtree.

Ledger Subsystem with Ethereum
------------------------------

**bbc1/core/ethereum/bbc_ethereum.py** contains an abstraction of
BBcAnchor smart contract that store roots of transaction Merkle trees.
It also provides verify function that takes a Merkle subtree for
verification independent from BBc-1.

**bbc1/core/ethereum/contracts/BBcAnchor.sol** is the solidity source
code of the BBcAnchor smart contract.

Subsystem Tools
---------------

**bbc1/core/subsystem_tool_lib.py** contains the base class definition
for creating a subsystem tool.

**utils/eth_subsytem_tool.py** is the subsystem tool for the ledger
subsystem with Ethereum. See README at **bbc1/core/ethereum** for detail
instruction.

How to Use This Module
----------------------

The following instructions assume that the command ‘python’ and ‘pip’
run python3 and pip3, respectively.

Product (or late-development stage)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Install

::

   $ pip install ledger-subsystem

or, during late-development stage,

::

   $ python setup.py sdist
   $ pip install dist/leger_subsystem-<version>.tar.gz

2. Use a subsystem tool to set up and use the module.

Development
~~~~~~~~~~~

1. Clone this to your environment, next to BBc-1 Core source code tree.
2. Install requirements

::

   $ pip install -r requirements.txt

3. Copy the source code tree of this module onto that of BBc-1 Core (do
   this everytime after modification).

::

   $ python devmerge.py

4. Use a subsystem tool to set up and use the module.

Notes
~~~~~

From version 0.13, we moved from populus/geth environment to
brownie/infura.io environment for the ledger subsystem with Ethereum.
brownie 1.0.0b6 has a problem working with infura.io, and pre 1.0.0b7
installation requires to clone the tests branch from github.

::

   $ git clone -b tests https://github.com/HyperLink-Technology/brownie.git
