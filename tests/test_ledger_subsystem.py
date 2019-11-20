# -*- coding: utf-8 -*-
"""
This test is performed on ledger subsystem with Ethereum, over 'development'
network of brownie. This test takes approximately 70 seconds to complete.
"""
import pytest
import hashlib
import os
import time

import sys
sys.path.extend(["../"])
import bbc1

TEST_CONFIG_FILE = 'test_config.json'

from bbc1.core import bbclib
from bbc1.core import ledger_subsystem, bbc_stats, bbc_network, bbc_config
from bbc1.core.ethereum import bbc_ethereum


domain_id1 = bbclib.get_new_id("test_domain1")
domain_id2 = bbclib.get_new_id("test_domain2")


class Args:

    def __init__(self):

        self.workingdir = bbc_config.DEFAULT_WORKING_DIR
        self.config = TEST_CONFIG_FILE


class DummyCore:
    class UserMessageRouting:
        def add_domain(self, domain_id):
            pass

        def remove_domain(self, domain_id):
            pass

    def __init__(self):
        self.user_message_routing = DummyCore.UserMessageRouting()
        self.stats = bbc_stats.BBcStats()


@pytest.fixture()
def default_config():

    args = Args()
    config = bbc_ethereum.setup_config(args.workingdir, args.config,
            'development')
    conf = config.get_config()

    db_conf = {
        "db_type": "sqlite",
        "db_name": "bbc_ledger.sqlite",
        "replication_strategy": "all",
        "db_servers": [
            {
                "db_addr": "127.0.0.1",
                "db_port": 3306,
                "db_user": "user",
                "db_pass": "pass"
            }
        ]
    }

    domain_id1_conf = {
        'storage': {
            'type': 'internal',
        },
        'db': db_conf,
        'use_ledger_subsystem': True,
        'ledger_subsystem': {
            'subsystem': 'ethereum',
            'max_transactions': 100,
            'max_seconds': 30,
        },
    }
    domain_id2_conf = {
        'storage': {
            'type': 'internal',
        },
        'db': db_conf,
        'use_ledger_subsystem': True,
        'ledger_subsystem': {
            'subsystem': 'ethereum',
            'max_transactions': 100,
            'max_seconds': 30,
        },
    }

    conf['domains'][domain_id1.hex()] = domain_id1_conf
    conf['domains'][domain_id2.hex()] = domain_id2_conf

    return config


def test_ledger_subsystem(default_config):

    bbc_ethereum.setup_deploy(default_config)

    prevdir = os.getcwd()
    os.chdir(bbc1.__path__[0] + '/core/ethereum')

    conf = default_config.get_config()

    os.chdir('..')

    networking = bbc_network.BBcNetwork(core=DummyCore(),
            config=default_config, p2p_port=6641)
    networking.create_domain(domain_id=domain_id1)

    ls = ledger_subsystem.LedgerSubsystem(default_config,
            networking=networking, domain_id=domain_id1, enabled=True)
    eth = bbc_ethereum.BBcEthereum(
        conf['ethereum']['network'],
        private_key=conf['ethereum']['private_key'],
        contract_address=conf['ethereum']['contract_address']
    )

    for i in range(150):
        ls.register_transaction(hashlib.sha256(i.to_bytes(4, 'big')).digest())

    print("\n30-second interval for trigger Merkle tree creation.")
    for i in range(6, 0, -1):
        print("continuing to sleep. countdown", i)
        time.sleep(5)

    i = 300
    j = ls.verify_transaction(hashlib.sha256(i.to_bytes(4, 'big')).digest())

    assert not j['result']

    for i in range(150):
        digest = hashlib.sha256(i.to_bytes(4, 'big')).digest()
        j = ls.verify_transaction(digest)
        assert j['result']
        assert eth.verify(digest, j['subtree']) > 0

    # -- test in another domain
    networking.create_domain(domain_id=domain_id2)
    ls = ledger_subsystem.LedgerSubsystem(default_config,
            networking=networking, domain_id=domain_id2, enabled=True)

    i = 100
    j = ls.verify_transaction(hashlib.sha256(i.to_bytes(4, 'big')).digest())

    assert not j['result']

    i = 99
    digest = hashlib.sha256(i.to_bytes(4, 'big')).digest()
    ls.register_transaction(digest)

    print("31-second interval for trigger Merkle tree creation.")
    time.sleep(1)
    for i in range(6, 0, -1):
        print("continuing to sleep. countdown", i)
        time.sleep(5)

    j = ls.verify_transaction(digest)
    assert j['result']
    assert eth.verify(digest, j['subtree']) > 0

    block_no, root = eth.verify_and_get_root(digest, j['subtree'])
    assert block_no == eth.test(root)

    os.chdir(prevdir)


# end of tests/test_ledger_subsystem_.py
