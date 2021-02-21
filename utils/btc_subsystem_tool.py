#!/bin/sh
""":" .

exec python "$0" "$@"
"""
# -*- coding: utf-8 -*-
from gevent import monkey
monkey.patch_all()

import sys
sys.path.extend(["../"])
from bbc1.core import bbclib, bbc_config, subsystem_tool_lib
from bbc1.core.bitcoin import bbc_bitcoin
import bbc1


class BitcoinSubsystemTool(subsystem_tool_lib.SubsystemTool):

    def __init__(self):
        super().__init__(
            name='Bitcoin',
            tool='btc_subsystem_tool.py',
            version='0.15.1'
        )

    def _add_additional_arguments(self):
        # btcgw command
        parser = self.subparsers.add_parser('btcgw',
                help='Initialize btcgw environment')
        parser.add_argument('server', action='store',
                help='btcgw server name (e.g. https://api.btcgw.example.com)')
        parser.add_argument('apikey', action='store',
                help='btcgw API Key')

    def _verify_by_subsystem(self, args, digest, spec, subtree):
        if spec[b'subsystem'] != b'bitcoin':
            print("Failed: not stored in an Bitcoin subsystem.")
            return 0
        print(f"Verified: Digest {digest.hex()[:10]}... (root={spec[b'root'].hex()}) is found in Bitcoin {spec[b'chain'].decode()} with transaction ID {spec[b'transaction'].decode()}.")
        return 1


if __name__ == '__main__':
    subsystem_tool = BitcoinSubsystemTool()
    args = subsystem_tool.parse_arguments()
    bbcConfig = bbc_bitcoin.setup_config(args.workingdir, args.config)

    if args.command_type == 'btcgw':
        bbc_bitcoin.setup_btcgw(bbcConfig, args.server, args.apikey)

    sys.exit(0)

# end of utils/btc_subsystem_tool.py
