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
from brownie import *
import hashlib
import json
import os
import subprocess
import time

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


def setup_account(bbcConfig, private_key):
    """Sets the specified Ethereum account to be used in the ledger subsystem.

    Args:
        bbcConfig (BBcConfig): The configuration object.
        private_key (str): The private key of the account in hex string.

    """
    config = bbcConfig.get_config()
    config['ethereum']['private_key'] = private_key

    prevdir = chdir_to_core_path()
    bbcConfig.update_config()
    os.chdir(prevdir)


def setup_brownie(infura_project_id):
    """Sets up a brownie environment for Ethereum ledger subsytem.
        Initializes the environment and compiles BBcAnchor contract.

    Args:
        infura_project_id (str): INFURA project ID.
            To be used for setting up 'ropsten' and 'mainnet' networks.

    """
    prevdir = chdir_to_this_filepath()
    subprocess.call(['brownie', 'init'])

    if os.path.exists('brownie-config.json'):

        f = open('brownie-config.json', 'r')
        jBrow = json.load(f)
        f.close()

        jRopsten = {
            'host': 'https://ropsten.infura.io/v3/' + infura_project_id,
            'broadcast_reverting_tx': False,
        }
        jMainnet = {
            'host': 'https://mainnet.infura.io/v3/' + infura_project_id,
            'broadcast_reverting_tx': False,
        }
    
        jNetworks = jBrow['networks']
        jNetworks['ropsten'] = jRopsten
        jNetworks['mainnet'] = jMainnet

        f = open('brownie-config.json', 'w')
        json.dump(jBrow, f, indent=2)
        f.close()

    subprocess.call(['brownie', 'compile'])
    os.chdir(prevdir)


def setup_config(working_dir, file_name, network_name):
    """Sets Ethereum brownie configuration.

    Args:
        working_dir (str): The working directory of BBc-1 core.
        file_name (str): The file name of BBc-1 core configuration file.
        network_name (str): The name of the brownie network.

    """

    prevdir = chdir_to_core_path()

    bbcConfig = bbc_config.BBcConfig(working_dir,
            os.path.join(working_dir, file_name))
    config = bbcConfig.get_config()

    isUpdated = False

    if not 'ethereum' in config or not 'network' in config['ethereum']:
        config['ethereum'] = {
            'network': network_name,
            'private_key': '',
            'contract_address': '',
        }
        isUpdated = True

    elif config['ethereum']['network'] != network_name:
        config['ethereum']['network'] = network_name
        isUpdated = True

    if isUpdated:
        bbcConfig.update_config()

    os.chdir(prevdir)

    return bbcConfig


def setup_deploy(bbcConfig):
    """Deploys BBcAnchor contract to Ethereum ledger subsystem.

    Args:
        bbcConfig (BBcConfig): The configuration object.

    """

    prevdir = chdir_to_this_filepath()

    config = bbcConfig.get_config()
    bbcEthereum = BBcEthereum(config['ethereum']['network'],
            private_key=config['ethereum']['private_key'])

    contract_address = config['ethereum']['contract_address']
    if contract_address != '':
        config['ethereum']['previous_contract_address'] = contract_address

    config['ethereum']['contract_address'] = bbcEthereum.get_contract_address()

    os.chdir('..')
    bbcConfig.update_config()
    os.chdir(prevdir)


def setup_new_account(bbcConfig):
    """Creates a new Ethereum account to be used in the ledger subsystem.

    Args:
        bbcConfig (BBcConfig): The configuration object.

    """

    prevdir = chdir_to_this_filepath()

    config = bbcConfig.get_config()

    project.load('.')
    network.connect(config['ethereum']['network'])

    accounts.add()
    config['ethereum']['private_key'] = accounts[0].private_key

    os.chdir('..')
    bbcConfig.update_config()
    os.chdir(prevdir)


def setup_test():
    """Tests BBcAnchor contract.
    """

    prevdir = chdir_to_this_filepath()
    subprocess.call(['brownie', 'test'])
    os.chdir(prevdir)


class BBcEthereum:

    """Abstraction of an Ethereum version of a proof-of-existnce contract.
    """

    call_count = 0

    def __init__(self, network_name, private_key=None, contract_address=None):
        """Initializes the object.

        Args:
            network_name (str): The name of the brownie network.
            private_key (str): The private key of the account. None by default.
                If None, default accounts[0] of the network is assumed.
            contract_address (str): The deployed contract. None by default.
                If None, a new contract is deployed.

        """

        if BBcEthereum.call_count <= 0:
            project.load('.')
            network.connect(network_name)
            if private_key is not None:
                accounts.add(private_key)

        BBcEthereum.call_count += 1

        if contract_address is None:
            accounts[0].deploy(project.BBcAnchor)
        else:
            project.BBcAnchor.at(contract_address)

        self.account = None if len(accounts) <= 0 else accounts[0]
        self.anchor = project.BBcAnchor[0]


    def blockingSet(self, digest):
        """Registers a digest in the contract.

        Args:
            digest (bytes or int): The digest to register.

        """

        if type(digest) == bytes:
            digest0 = int.from_bytes(digest, 'big')
        else:
            digest0 = digest

        self.anchor.store(digest0, {'from': self.account})


    def get_contract_address(self):
        """Gets the contract address.

        Returns:
            address (str): The address of the deployed BBcAnchor contract.

        """

        return self.anchor.address


    def test(self, digest):
        """Verifies whether the digest (Merkle root) is registered or not.

        Args:
            digest (bytes or int): The digest (Merkle root) to test existence.

        Returns:
            block_number (int): The block number upon registration.
                0 if not found.

        """

        if type(digest) == bytes:
            digest0 = int.from_bytes(digest, 'big')
        else:
            digest0 = digest

        return self.anchor.getStored(digest0)


    def verify(self, digest, subtree):
        """Verifies whether the digest is included in the Merkle tree.

        Args:
            digest (bytes or int): The digest to test existence.
            subtree (list): The Merkle subtree to calculate the root.

        Returns:
            block_number (int): The block number upon registration.
                0 if not found.

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
    if len(sys.argv) == 2:
        a = BBcEthereum(sys.argv[1])
    elif len(sys.argv) == 3:
        a = BBcEthereum(sys.argv[1], private_key=sys.argv[2])
    elif len(sys.argv) == 4:
        a = BBcEthereum(sys.argv[1], private_key=sys.argv[2],
                contract_address=sys.argv[3])

    a.blockingSet(0x1234)
    print(a.test(0x1230))
    print(a.test(0x1234))

    a.blockingSet(b'\x43\x21')
    print(a.test(0x4321))
    print(a.test(b'\x43\x21'))


# end of core/ethereum/bbc_ethereum.py
