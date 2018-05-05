# -*- coding: utf-8 -*-
"""
Copyright (c) 2018 beyond-blockchain.org.

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
import os

import sys
sys.path.append(["../"])
from bbc1.core import bbclib, bbc_app, bbc_config
from bbc1.core.message_key_types import KeyType


def wait_check_result_msg_type(callback, msg_type):
    dat = callback.synchronize()
    if dat is None:
        print("Error: subsystem is not ready; "
                "make sure of the following conditions:")
        print("  * blockchain node (i.e., geth/bitcoind) is running.")
        print("  * bbc_core.py is started with '--ledgersubsystem'.")
        print("  * subsystem is configured with config_tree command.")
        sys.exit(1)
    if dat[KeyType.command] != msg_type:
        sys.stderr.write("XXXXXX not expected result: %d <=> %d(received)\n"
                % (msg_type, dat[KeyType.command]))
    return dat


class SubsystemTool:
    """
    Abstraction of BBc-1 ledger subsystem tool.
    """
    def __init__(self, name=None, tool=None, version=None):

        self.name = name
        self.tool = tool
        self.version = version

        self.domain_id = None
        self.client = None

        self.argparser = argparse.ArgumentParser(
                description=self._description_string())
        self.subparsers = self.argparser.add_subparsers(
                dest='command_type', help='select commands')


    def parse_arguments(self):

        self.argparser.add_argument('-4', '--ip4address', type=str,
                default="127.0.0.1", help='bbc_core IP address (IPv4)')
        self.argparser.add_argument('-6', '--ip6address', type=str,
                help='bbc_core IP address (IPv6)')
        self.argparser.add_argument('-c', '--config', type=str,
                default=bbc_config.DEFAULT_CONFIG_FILE,
                help='config file name')
        self.argparser.add_argument('-cp', '--coreport', type=int,
                default=bbc_config.DEFAULT_CORE_PORT,
                help='port number of bbc_core')
        self.argparser.add_argument('-d', '--domain_id', type=str,
                default=None,
                help='domain_id in hexadecimal')
        self.argparser.add_argument('-k', '--node_key', type=str,
                default=None,
                help='path to node key pem file')
        self.argparser.add_argument('-v', '--version', action='store_true',
                help='print version and exit')
        self.argparser.add_argument('-w', '--workingdir', type=str,
                default=bbc_config.DEFAULT_WORKING_DIR,
                help='working directory name')

        # config_demo command
        self.subparsers.add_parser('config_demo',
                help='Create a demo domain and config_tree (common command)')

        # config_tree command
        parser = self.subparsers.add_parser('config_tree',
                help='Configure how to form Merkle trees (common command)')
        parser.add_argument('transactions', type=int, action='store',
                help='# of transactions to wait before forming a Merkle tree')
        parser.add_argument('seconds', type=int, action='store',
                help='# of seconds to wait before forming a Merkle tree')

        # disable command
        self.subparsers.add_parser('disable',
                help='Disable ledger subsystem (common command)')

        # enable command
        self.subparsers.add_parser('enable',
                help='Enable ledger subsystem (common command)')

        # register_demo command
        parser = self.subparsers.add_parser('register_demo',
                help="Register dummy transaction_id's (common command)")
        parser.add_argument('count', type=int, action='store',
                help="# of dummy transaction_id's to register "
                "for testing/demo")

        # verify command
        parser = self.subparsers.add_parser('verify',
                help='Verify a transaction (common command)')
        parser.add_argument('txid', action='store',
                help='transaction_id to verify (in hexadecimal)')

        self._add_additional_arguments()

        args = self.argparser.parse_args()

        if args.version:
            print(self.tool + ' ' + self.version)
            sys.exit(0)

        if args.domain_id:
            self.domain_id = bbclib.convert_idstring_to_bytes(args.domain_id)

        if args.node_key and os.path.exists(args.node_key):
            self._run_client(args)
            self.client.set_node_key(args.node_key)

        if args.command_type == 'enable':
            self._run_client(args)
            self._enable()
            sys.exit(0)

        if args.command_type == 'disable':
            self._run_client(args)
            self._disable()
            sys.exit(0)

        if args.command_type == 'verify':
            self._run_client(args)
            self._verify(args, bbclib.convert_idstring_to_bytes(args.txid))
            sys.exit(0)

        if args.command_type == 'config_tree':
            self._check_domain_id()
            self._config_tree(args)
            sys.exit(0)

        if args.command_type == 'config_demo':
            self.domain_id = bbclib.get_new_id("dummy_domain")
            self._run_client(args)
            self._config_demo(args)
            sys.exit(0)

        if args.command_type == 'register_demo':
            self._run_client(args)
            self._register_demo(args.count)
            sys.exit(0)

        return args


    def _add_additional_arguments(self):
        pass


    def _check_domain_id(self):
        if self.domain_id is None:
            print("Error: please specify domain_id with '-d DOMAIN_ID'.")
            sys.exit(1)


    def _config_demo(self, args):
        self.client.domain_setup(self.domain_id)
        dat = wait_check_result_msg_type(self.client.callback,
                bbclib.MsgType.RESPONSE_SETUP_DOMAIN)
        if KeyType.reason in dat:
            print("Failed:", dat[KeyType.reason])
        print("domain_id:")
        print(bbclib.convert_id_to_string(self.domain_id))

        args.transactions = 100
        args.seconds = 30
        self._config_tree(args)


    def _config_tree(self, args):

        prevdir = os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))

        bbcConfig = bbc_config.BBcConfig(args.workingdir,
                os.path.join(args.workingdir, args.config))
        config = bbcConfig.get_domain_config(self.domain_id)

        config['use_ledger_subsystem'] = True
        if 'ledger_subsystem' not in config:
            config['ledger_subsystem'] = {
                'subsystem': self.name.lower(),
                'max_transactions': 0,
                'max_seconds': 0
            }
        config['ledger_subsystem']['max_transactions'] = args.transactions
        config['ledger_subsystem']['max_seconds'] = args.seconds

        bbcConfig.update_config()
        os.chdir(prevdir)
        print("You may want to restart bbc_core.py"
                " (with '--ledgersubsystem').")


    def _description_string(self):
        return "Set up, enable and disable BBc-1 ledger subsystem with %s." \
                % (self.name)


    def _disable(self):
        self.client.manipulate_ledger_subsystem(enable=False,
                domain_id=self.domain_id)
        dat = wait_check_result_msg_type(self.client.callback,
                bbclib.MsgType.RESPONSE_MANIP_LEDGER_SUBSYS)
        if KeyType.reason in dat:
            print("Failed:", dat[KeyType.reason])


    def _enable(self):
        self.client.manipulate_ledger_subsystem(enable=True,
                domain_id=self.domain_id)
        dat = wait_check_result_msg_type(self.client.callback,
                bbclib.MsgType.RESPONSE_MANIP_LEDGER_SUBSYS)
        if KeyType.reason in dat:
            print("Failed:", dat[KeyType.reason])


    def _run_client(self, args):
        self._check_domain_id()
        if self.client is None:
            if args.ip4address:
                addr = args.ip4address
            if args.ip6address:
                addr = args.ip6address
            self.client = bbc_app.BBcAppClient(host=addr, port=args.coreport,
                    multiq=False, loglevel='all')
            self.client.set_user_id(bbclib.get_new_id('.subsystem_tool',
                    include_timestamp=False))
            self.client.set_domain_id(self.domain_id)
            self.client.set_callback(bbc_app.Callback())
            ret = self.client.register_to_core()
            assert ret


    def _register_demo(self, count):
        print("transaction_id's:")

        for i in range(count):
            txid = bbclib.get_new_id("dummy %d" % (i))
            self.client.register_in_ledger_subsystem(None, txid)
            dat = wait_check_result_msg_type(self.client.callback,
                    bbclib.MsgType.RESPONSE_REGISTER_HASH_IN_SUBSYS)
            print(bbclib.convert_id_to_string(txid))


    def _verify(self, args, transaction_id):
        self.client.verify_in_ledger_subsystem(None, transaction_id)
        dat = wait_check_result_msg_type(self.client.callback,
                bbclib.MsgType.RESPONSE_VERIFY_HASH_IN_SUBSYS)

        if dat[KeyType.merkle_tree] == {}:
            print("Failed: ledger subsystem is not enabled.")
            return

        dic = dat[KeyType.merkle_tree]
        if dic[b'result'] == False:
            print("Failed: transaction is not found.")
            return

        block_no = self._verify_by_subsystem(args, transaction_id,
                dic[b'spec'], dic[b'subtree'])

        if block_no <= 0:
            print("Failed: transaction is not found.")
        else:
            print("Verified: Merkle root is stored at block %d." % (block_no))


    def _verify_by_subsystem(self, digest, spec, subtree):
        pass


# end of core/subsystem_tool_lib.py
