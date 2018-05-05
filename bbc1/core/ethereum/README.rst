Ledger subsystem with Ethereum for BBc-1
========================================

Files in this directory supports the ledger subsystem with Ethereum
blockchain for BBc-1. Currently supports local geth chain only.

Ledger subsystem
----------------

-  **bbc1/core/ethereum/bbc_ethereum.py**

   -  abstraction of BBcAnchor smart contract that would store Merkle
      roots of transactions.
   -  also provides setup library functions for Populus environment and
      geth Ethereum node.
   -  also provides verify function that takes a Merkle subtree for
      independent verification from BBc-1.

-  **bbc1/core/ethereum/contracts/BBcAnchor.sol**

   -  The BBcAnchor smart contract.

-  **utils/eth_subsystem_tool.py**

   -  sets up Populus environment and geth Ethereum node. See usage
      below.

Dependencies
------------

-  populus 1.10.1 (note that rlp==0.5.1), 1.11.0-2.1.0 (rlp==0.6.0)
   (pip-installed)
-  geth (go ethereum) 1.7.2-1.8.7 (install with apt or brew)
-  solc (solidity) 0.4.17-0.4.23 (install with apt or brew)

How to use
----------

For the example below, we assume that BBc-1 Core and the ledger
subsystem are pip-installed, and ‘bbc_core.py’ is running at the user’s
home directory (the “config.json” file resides under “~/.bbc1”).

1. Set up populus environment

::

   $ eth_subsystem_tool.py -w ~/.bbc1 populus

2. Set up genesis block of a local geth chain

::

   $ eth_subsytem_tool.py -w ~/.bbc1 genesis

3. Set up a new Ethereum account

::

   $ eth_subsystem_tool.py -w ~/.bbc1 new_account <passphrase>

4. Run the local geth chain

::

   $ eth_subsystem_tool.py -w ~/.bbc1 run_geth

For the first execution, this would take some tens of minutes for mining
to be started.

5. Deploy BBcAnchor smart contract

::

   $ eth_subsystem_tool.py -w ~/.bbc1 deploy

You are all set, and you can run ledger_subsystem with enabled=True
argument or enable() it.

If your geth chain has already been mined, then you may want to try

::

   $ eth_subsystem_tool.py -w ~/.bbc1 auto <passphrase>

to automatically set up everything (but beware that the contract address
will be overwritten. Consider this as a testing feature, useful when
BBc-1 configuration has been erased).

When you want to stop the local geth chain,

::

   $ eth_subsystem_tool.py -w ~/.bbc1 stop_geth

When you want to resume, just

::

   $ eth_subsystem_tool.py -w ~/.bbc1 run_geth

You do not need to set up an account or deploy the contract again. The
information is all written into the config file of BBc-1 core.

Tests
-----

-  **tests/test_bbc_ethereum.py** — run prior to
   test_ledger_subsystem.py
-  **tests/test_ledger_subsystem.py**
