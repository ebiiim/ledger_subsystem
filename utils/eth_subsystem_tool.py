#!/bin/sh
""":" .

exec python "$0" "$@"
"""
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
import gevent
from gevent import monkey
monkey.patch_all()

import argparse
from brownie import *
import json
import os
import subprocess
import time

import sys
sys.path.extend(["../"])
from bbc1.core import bbclib, bbc_config, subsystem_tool_lib
from bbc1.core.ethereum import bbc_ethereum
import bbc1


class EthereumSubsystemTool(subsystem_tool_lib.SubsystemTool):

    def __init__(self):
        super().__init__(
            name='Ethereum',
            tool='eth_subsystem_tool.py',
            version='0.13.1'
        )


    def _add_additional_arguments(self):
        self.argparser.add_argument('-n', '--network', type=str,
                default='ropsten',
                help='network name (ropsten by default)')

        # account command
        parser = self.subparsers.add_parser('account',
                help='Set an Ethereum account')
        parser.add_argument('private_key', action='store',
                help='Private key of the account')

        # auto command
        parser = self.subparsers.add_parser('auto',
                help='Automatically set up everything')
        parser.add_argument('project_id', action='store',
                help='INFURA project ID')
        parser.add_argument('private_key', action='store',
                help='Private key of the account')

        # deploy command
        self.subparsers.add_parser('deploy', help='Deploy the anchor contract')

        # new_account command
        parser = self.subparsers.add_parser('new_account',
                help='Create a new Ethereum account')

        # brownie command
        parser = self.subparsers.add_parser('brownie',
                help='Initialize brownie and infura environment')
        parser.add_argument('project_id', action='store',
                help='INFURA project ID')

        # test command
        self.subparsers.add_parser('test', help='Test the anchor contract')


    def _verify_by_subsystem(self, args, digest, spec, subtree):

        if spec[b'subsystem'] != b'ethereum':
            print("Failed: not stored in an Ethereum subsystem.")
            return 0

        bbcConfig = bbc_ethereum.setup_config(args.workingdir, args.config,
                args.network)
        config = bbcConfig.get_config()

        prevdir = os.getcwd()
        os.chdir(bbc1.__path__[0] + '/core/ethereum')

        eth = bbc_ethereum.BBcEthereum(
            config['ethereum']['network'],
            config['ethereum']['private_key'],
            contract_address=spec[b'contract_address'].decode('utf-8')
        )

        os.chdir(prevdir)

        return eth.verify(digest, subtree)


if __name__ == '__main__':

    subsystem_tool = EthereumSubsystemTool()
    args = subsystem_tool.parse_arguments()
    bbcConfig = bbc_ethereum.setup_config(args.workingdir, args.config,
            args.network)

    if args.command_type == 'auto':
        print("Setting up brownie.")
        bbc_ethereum.setup_brownie(args.project_id)
        print("Setting up an Ethereum account.")
        bbc_ethereum.setup_account(bbcConfig, args.private_key)
        print("Deploying the anchor contract.")
        bbc_ethereum.setup_deploy(bbcConfig)

    elif args.command_type == 'brownie':
        bbc_ethereum.setup_brownie(args.project_id)

    elif args.command_type == 'test':
        bbc_ethereum.setup_test()

    elif args.command_type == 'new_account':
        bbc_ethereum.setup_new_account(bbcConfig)
        print("private_key (copy and save somewhere):")
        print(accounts[0].private_key)
        print("address (copy and save somewhere):")
        print(accounts[0].address)

    elif args.command_type == 'account':
        bbc_ethereum.setup_account(bbcConfig, args.private_key)

    elif args.command_type == 'deploy':
        bbc_ethereum.setup_deploy(bbcConfig)

    sys.exit(0)


# end of utils/eth_subsystem_tool.py
