Ledger subsystem with Ethereum for BBc-1
========================================

Files in this directory supports the ledger subsystem with Ethereum
blockchain for BBc-1. Currently supports brownie, with infura.io to
access to ropsten test network and mainnet of Ethereum.

Ledger subsystem
----------------

-  **bbc1/core/ethereum/bbc_ethereum.py**

   -  abstraction of BBcAnchor smart contract that would store Merkle
      roots of transactions.
   -  also provides setup library functions for brownie environment and
      to use infura.io projects.
   -  also provides verify function that takes a Merkle subtree for
      independent verification from BBc-1.

-  **bbc1/core/ethereum/contracts/BBcAnchor.sol**

   -  The BBcAnchor smart contract.

-  **utils/eth_subsystem_tool.py**

   -  sets up brownie environment and to use infura.io projects to
      access Ethereum networks. See usage below.

Dependencies
------------

-  brownie>=1.0.0b7 (pip-installed)
-  solc (solidity) 0.5 (install with apt or brew) (actual compilation
   uses py-solc-x installed with brownie, but requires depedencies for
   solc anyway)

How to use
----------

For the example below, we assume that BBc-1 Core and the ledger
subsystem are pip-installed, and ‘bbc_core.py’ is running at the user’s
home directory (the “config.json” file resides under “~/.bbc1”). The
default Ethereum network is ropsten test network.

1. Set up brownie environment

::

   $ eth_subsystem_tool.py -w ~/.bbc1 brownie <infura.io project ID>

2. Set up a new Ethereum account (if you do not have one yet)

::

   $ eth_subsystem_tool.py -w ~/.bbc1 new_account

If you have already got an account, and know its private key, you can
set it using “account” command of eth_subsystem_tool.py.

3. Load the account with ETH from the specified network

For that, for ropsten, faucets like https://faucet.ropsten.be can be
used. The balance can be confirmed with “balance” command of
eth_subsystem_tool.py.

4. Deploy BBcAnchor smart contract

::

   $ eth_subsystem_tool.py -w ~/.bbc1 deploy

You are all set, and you can run ledger_subsystem with enabled=True
argument or enable() it. Or you may want to try “enable” command of
eth_subsystem_tool.py for that.

If you are sure, then you may want to try

::

   $ eth_subsystem_tool.py -w ~/.bbc1 auto <infura project ID> <private_key>

to automatically set up everything with an existing Ethereum account
with sufficient ETH balance at the specified network (but beware that
the contract address will be overwritten. Consider this as a testing
feature, useful when BBc-1 configuration has been erased).

You do not need to set up an account or deploy the contract again. The
information is all written into the config file of BBc-1 core.

Tests
-----

-  **tests/test_bbc_ethereum1.py**
-  **tests/test_bbc_ethereum2.py**
-  **tests/test_bbc_ethereum3.py**
-  **tests/test_ledger_subsystem.py**
