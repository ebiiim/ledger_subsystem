# -*- coding: utf-8 -*-
"""
Copyright (c) 2017 beyond-blockchain.org.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import binascii
import hashlib
import json
import os
from populus import Project
from populus.utils.wait import wait_for_transaction_receipt
import subprocess
from web3 import Web3

import sys
sys.path.extend(["../../../"])
from bbc1.core import bbc_config


def chdir_to_core_path():
    prevdir = chdir_to_this_filepath()
    os.chdir('..')
    return prevdir


def chdir_to_this_filepath():
    prevdir = os.getcwd()
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    return prevdir


def setup_account(bbcConfig, account, passphrase):
    """
    Sets the specified Ethereum account to be used in the ledger subsystem.

    :param bbcConfig: configuration object
    :param account: Ethereum account in hexadecimal prefixed with '0x'
    :param passphrase: Passphrase to unlock the account
    :return:
    """
    config = bbcConfig.get_config()
    config['ethereum']['account'] = account
    config['ethereum']['passphrase'] = passphrase

    prevdir = chdir_to_core_path()
    bbcConfig.update_config()
    os.chdir(prevdir)


def setup_config(workingdir, filename, networkid, port, log):

    prevdir = chdir_to_core_path()

    bbcConfig = bbc_config.BBcConfig(workingdir,
            os.path.join(workingdir, filename))
    config = bbcConfig.get_config()

    isUpdated = False

    if not 'ethereum' in config:
        config['ethereum'] = {
            'chain_id': networkid,
            'port': port,
            'log': log,
            'account': '',
            'passphrase': '',
            'contract_address': '',
        }
        isUpdated = True

    elif config['ethereum']['chain_id'] != networkid:
        config['ethereum']['chain_id'] = networkid
        isUpdated = True

    elif config['ethereum']['port'] != port:
        config['ethereum']['port'] = port
        isUpdated = True

    elif config['ethereum']['log'] != log:
        config['ethereum']['log'] = log
        isUpdated = True

    if isUpdated:
        bbcConfig.update_config()

    os.chdir(prevdir)

    return bbcConfig


def setup_deploy(bbcConfig):
    """
    Deploys BBcAnchor contract to Ethereum ledger subsystem.

    :param bbcConfig: configuration object
    :return:
    """
    prevdir = chdir_to_this_filepath()
    config = bbcConfig.get_config()
    bbcEthereum = BBcEthereum(config['ethereum']['account'],
            config['ethereum']['passphrase'])

    contract_address = config['ethereum']['contract_address']
    if contract_address != '':
        config['ethereum']['previous_contract_address'] = contract_address

    config['ethereum']['contract_address'] = bbcEthereum.get_contract_address()


    os.chdir('..')
    bbcConfig.update_config()
    os.chdir(prevdir)


def setup_genesis(bbcConfig):
    """
    Creates the genesis block of Ethereum ledger subsystem.

    :param bbcConfig: configuration object
    :return:
    """
    prevdir = chdir_to_this_filepath()
    config = bbcConfig.get_config()

    jGenesis = {
      "config": {
        "chainId": config['ethereum']['chain_id'],
        "homesteadBlock": 0,
        "eip155Block": 0,
        "eip158Block": 0
      },
      "difficulty": "0x200",
      "gasLimit": "2100000",
      "alloc": {
      }
    }

    f = open('genesis.json', 'w')
    json.dump(jGenesis, f, indent=2)
    f.close()

    subprocess.call(['geth', 'init', 'genesis.json'])
    os.chdir(prevdir)


def setup_new_account(bbcConfig, passphrase):
    """
    Creates a new Ethereum account to be used in the ledger subsystem.

    :param bbcConfig: configuration object
    :param passphrase: Passphrase to unlock the new account
    :return:
    """
    prevdir = chdir_to_core_path()
    PASSWORD_FILE = '_password'

    f = open(PASSWORD_FILE, 'w')
    f.write(passphrase + '\n')
    f.close()

    bytes = subprocess.check_output(
        ['geth', 'account', 'new', '--password', PASSWORD_FILE]
    )

    config = bbcConfig.get_config()
    config['ethereum']['account'] = '0x' + bytes.decode('utf-8')[10:50]
    config['ethereum']['passphrase'] = passphrase
    bbcConfig.update_config()

    os.remove(PASSWORD_FILE)
    os.chdir(prevdir)


def setup_populus():
    """
    Sets up a Populus environment to communicate with Ethereum ledger subsytem.
    Initializes the environment and compiles BBcAnchor contract.

    :return:
    """
    prevdir = chdir_to_this_filepath()
    subprocess.call(['populus', 'init'])

    os.remove('contracts/Greeter.sol')
    os.remove('tests/test_greeter.py')

    if os.path.exists('populus.json'):

        f = open('populus.json', 'r')
        jPop = json.load(f)
        f.close()

        jBBcChain = {
          "chain": {
            "class": "populus.chain.ExternalChain"
          },
          "contracts": {
            "backends": {
              "JSONFile": {
                "$ref": "contracts.backends.JSONFile"
              },
              "Memory": {
                "$ref": "contracts.backends.Memory"
              },
              "ProjectContracts": {
                "$ref": "contracts.backends.ProjectContracts"
              },
              "TestContracts": {
                "$ref": "contracts.backends.TestContracts"
              }
            }
          },
          "web3": {
            "$ref": "web3.GethIPC"
          }
        }
    
        jChains = jPop['chains']
        jChains['bbc'] = jBBcChain

        f = open('populus.json', 'w')
        json.dump(jPop, f, indent=2)
        f.close()

    elif os.path.exists('project.json'):

        f = open('project.json', 'r')
        jPop = json.load(f)
        f.close()

        jBBcChain = {
          "chain": {
            "class": "populus.chain.ExternalChain"
          },
          "contracts": {
            "backends": {
              "JSONFile": {
                "class": "populus.contracts.backends.filesystem.JSONFileBackend",
                "priority": 10,
                "settings": {
                  "file_path": "./registrar.json"
                }
              },
              "Memory": {
                "class": "populus.contracts.backends.memory.MemoryBackend",
                "priority": 50
              },
              "ProjectContracts": {
                "class": "populus.contracts.backends.project.ProjectContractsBackend",
                "priority": 20
              },
              "TestContracts": {
                "class": "populus.contracts.backends.testing.TestContractsBackend",
                "priority": 40
              }
            }
          },
          "web3": {
            "provider": {
              "class": "web3.providers.ipc.IPCProvider"
            }
          }
        }
    
        jChains = dict()
        jChains['bbc'] = jBBcChain
        jPop['chains'] = jChains

        f = open('project.json', 'w')
        json.dump(jPop, f, indent=2)
        f.close()

    subprocess.call(['populus', 'compile'])
    os.chdir(prevdir)


def setup_run(bbcConfig):
    """
    Runs a geth Ethereum node.

    :param bbcConfig: configuration object
    :return:
    """
    config = bbcConfig.get_config()

    log = open(config['ethereum']['log'], 'a')

    proc = subprocess.Popen([
        'geth',
        '--networkid', str(config['ethereum']['chain_id']),
        '--port', str(config['ethereum']['port']),
        '--maxpeers', '0',
        '--nodiscover',
        '--etherbase', config['ethereum']['account'],
        '--mine',
        '--miner.threads', '1',
    ], stderr=log)

    config['ethereum']['pid'] = proc.pid

    prevdir = chdir_to_core_path()
    bbcConfig.update_config()
    os.chdir(prevdir)


def setup_stop(bbcConfig):
    """
    Stops a geth Ethereum node.

    :param bbcConfig: configuration object
    :return:
    """
    config = bbcConfig.get_config()

    subprocess.call(['kill', str(config['ethereum']['pid'])])

    config['ethereum']['pid'] = None

    prevdir = chdir_to_core_path()
    bbcConfig.update_config()
    os.chdir(prevdir)


def setup_test():
    """
    Tests BBcAnchor contract.

    :return:
    """
    prevdir = chdir_to_this_filepath()
    subprocess.call(['py.test', '.'])
    os.chdir(prevdir)


class BBcEthereum:
    """
    Abstraction of an Ethereum version of a proof of existnce contact.
    """
    def __init__(self, account, passphrase, contract_address=None):
        """
        Constructs the contract object.

        :param account: Ethereum account in hexadecimal prefixed with '0x'
        :param passphrase: Passphrase to unlock the account
        :param contract_address: Deployed contract (if None, it deploys one)
        :return:
        """
        project = Project()
        chain_name = "bbc"

        with project.get_chain(chain_name) as chain:

            AnchorFactory = chain.provider.get_contract_factory('BBcAnchor')

            chain.web3.personal.unlockAccount(account, passphrase)

            if contract_address is None:
                txid = AnchorFactory.deploy(
                    transaction={"from": account},
                    args=[]
                )
                contract_address = chain.wait.for_contract_address(txid)

            self.account = account
            self.anchor = AnchorFactory(address = contract_address)
            self.chain = chain


    def blockingSet(self, digest):
        """
        Registeres a digest in the contract.

        :param digest: Digest to register
        :return:
        """
        if type(digest) == bytes:
            digest0 = int.from_bytes(digest, 'big')
        else:
            digest0 = digest
        txid = self.anchor.transact(
            transaction={"from": self.account}
        ).store(digest0)
        self.chain.wait.for_receipt(txid)


    def get_contract_address(self):
        """
        Returns the contract address.

        :return: the contract address of the deployed BBcAnchor
        """
        return self.anchor.address


    def test(self, digest):
        """
        Verifies whether the digest (Merkle root) is registered or not.

        :param digest: Digest (Merkle root) to test existence
        :return: 0 if not found, otherwise the block number upon registration
        """
        if type(digest) == bytes:
            digest0 = int.from_bytes(digest, 'big')
        else:
            digest0 = digest
        return self.anchor.call().getStored(digest0)


    def verify(self, digest, subtree):
        """
        Verifies whether the digest is included in the registered Merkle tree.

        :param digest: Digest to test existence
        :param subtree: Merkle subtree to calculate the root
        :return: 0 if not found, otherwise the block number upon registration
        """
        for dic in subtree:
            if 'digest' in dic:
                digest0 = binascii.a2b_hex(dic['digest'])
                if dic['position'] == 'right':
                    dLeft = digest
                    dRight = digest0
                else:
                    dLeft = digest0
                    dRight = digest
                digest = hashlib.sha256(dLeft + dRight).digest()

            else:
                digest0 = binascii.a2b_hex(dic[b'digest'].decode())
                if dic[b'position'] == b'right':
                    dLeft = digest
                    dRight = digest0
                else:
                    dLeft = digest0
                    dRight = digest
                digest = hashlib.sha256(dLeft + dRight).digest()

        return self.test(digest)


if __name__ == '__main__':

    # simple test code and usage
    a = BBcEthereum(sys.argv[1], sys.argv[2], sys.argv[3])

    a.blockingSet(0x1234)
    print(a.test(0x1230))
    print(a.test(0x1234))

    a.blockingSet(b'\x43\x21')
    print(a.test(0x4321))
    print(a.test(b'\x43\x21'))


# end of core/ethereum/bbc_ethereum.py
