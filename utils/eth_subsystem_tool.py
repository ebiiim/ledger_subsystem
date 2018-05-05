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
import argparse
import json
import populus
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
            version='0.11.0'
        )


    def _add_additional_arguments(self):
        self.argparser.add_argument('-l', '--log', type=str,
                default=bbc_config.DEFAULT_ETHEREUM_LOG_FILE,
                help='geth log file name')
        self.argparser.add_argument('-n', '--networkid', type=int,
                default=bbc_config.DEFAULT_ETHEREUM_CHAIN_ID,
                help='geth network id number')
        self.argparser.add_argument('-gp', '--gethport', type=int,
                default=bbc_config.DEFAULT_ETHEREUM_GETH_PORT,
                help='geth port number')

        # account command
        parser = self.subparsers.add_parser('account',
                help='Set an Ethereum account')
        parser.add_argument('address', action='store',
                help='Address of the account')
        parser.add_argument('passphrase', action='store',
                help='Passphrase of the account')

        # auto command
        parser = self.subparsers.add_parser('auto',
                help='Automatically set up everything')
        parser.add_argument('passphrase', action='store',
                help='Passphrase of a new account')

        # deploy command
        self.subparsers.add_parser('deploy', help='Deploy the anchor contract')

        # genesis command
        self.subparsers.add_parser('genesis',
                help='Create Ethereum genesis block')

        # new_account command
        parser = self.subparsers.add_parser('new_account',
                help='Create a new Ethereum account')
        parser.add_argument('passphrase', action='store',
                help='Passphrase of the new account')

        # populus command
        self.subparsers.add_parser('populus',
                help='Initialize populus environment')

        # run_geth command
        self.subparsers.add_parser('run_geth', help='Run local geth node')

        # stop_geth command
        self.subparsers.add_parser('stop_geth', help='Stop local geth node')

        # test command
        self.subparsers.add_parser('test', help='Test the anchor contract')


    def _verify_by_subsystem(self, args, digest, spec, subtree):

        if spec[b'subsystem'] != b'ethereum':
            print("Failed: not stored in an Ethereum subsystem.")
            return 0

        bbcConfig = bbc_ethereum.setup_config(args.workingdir, args.config,
            args.networkid, args.gethport, args.log)
        config = bbcConfig.get_config()

        prevdir = os.getcwd()
        os.chdir(bbc1.__path__[0] + '/core/ethereum')

        eth = bbc_ethereum.BBcEthereum(
            config['ethereum']['account'],
            config['ethereum']['passphrase'],
            contract_address=spec[b'contract_address']
        )

        os.chdir(prevdir)

        return eth.verify(digest, subtree)


if __name__ == '__main__':

    subsystem_tool = EthereumSubsystemTool()
    args = subsystem_tool.parse_arguments()
    bbcConfig = bbc_ethereum.setup_config(args.workingdir, args.config,
            args.networkid, args.gethport, args.log)

    if args.command_type == 'auto':
        print("Setting up populus.")
        bbc_ethereum.setup_populus()
        print("Setting up an Ethereum genesis block.")
        bbc_ethereum.setup_genesis(bbcConfig)
        print("Setting up a new Ethereum account.")
        bbc_ethereum.setup_new_account(bbcConfig, args.passphrase)
        print("Starting a local geth node.")
        bbc_ethereum.setup_run(bbcConfig)
        print("10-second interval for mining.")
        time.sleep(10)
        print("Deploying the anchor contract.")
        bbc_ethereum.setup_deploy(bbcConfig)
        print("To stop the local geth node, "
                "type 'eth_subsystem_tool.py stop_geth'.")

    elif args.command_type == 'populus':
        bbc_ethereum.setup_populus()

    elif args.command_type == 'test':
        bbc_ethereum.setup_test()

    elif args.command_type == 'genesis':
        bbc_ethereum.setup_genesis(bbcConfig)

    elif args.command_type == 'new_account':
        bbc_ethereum.setup_new_account(bbcConfig, args.passphrase)

    elif args.command_type == 'account':
        bbc_ethereum.setup_account(bbcConfig, args.address, args.passphrase)

    elif args.command_type == 'run_geth':
        bbc_ethereum.setup_run(bbcConfig)

    elif args.command_type == 'stop_geth':
        bbc_ethereum.setup_stop(bbcConfig)

    elif args.command_type == 'deploy':
        bbc_ethereum.setup_deploy(bbcConfig)

    sys.exit(0)


# end of utils/eth_subsystem_tool.py
