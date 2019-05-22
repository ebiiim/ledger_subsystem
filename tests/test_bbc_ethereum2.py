# -*- coding: utf-8 -*-
import pytest
import json
import os
import subprocess
import time

import sys
sys.path.extend(["../"])
from bbc1.core import bbc_config
from bbc1.core.ethereum import bbc_ethereum
import bbc1

TEST_CONFIG_FILE = 'test_config.json'

from test_bbc_ethereum_const import TEST_PRIVATE_KEY
from test_bbc_ethereum_const import TEST_INFURA_PROJECT_ID


class Args:

    def __init__(self):

        self.workingdir = bbc_config.DEFAULT_WORKING_DIR
        self.config = TEST_CONFIG_FILE


@pytest.fixture()
def default_config():
    args = Args()
    return bbc_ethereum.setup_config(args.workingdir, args.config,
            'ropsten' if TEST_INFURA_PROJECT_ID != '' else 'development')


def test_setup_account(default_config):

    bbc_ethereum.setup_account(default_config, TEST_PRIVATE_KEY)

    prevdir = os.getcwd()
    os.chdir(bbc1.__path__[0] + '/core/' + bbc_config.DEFAULT_WORKING_DIR)

    f = open(TEST_CONFIG_FILE, 'r')
    config = json.load(f)
    f.close()

    assert config['ethereum']['private_key'] == TEST_PRIVATE_KEY

    os.chdir(prevdir)
    print("\n==> another account is set.")


def test_setup_deploy(default_config):

    bbc_ethereum.setup_deploy(default_config)

    prevdir = os.getcwd()
    os.chdir(bbc1.__path__[0] + '/core/' + bbc_config.DEFAULT_WORKING_DIR)

    f = open(TEST_CONFIG_FILE, 'r')
    config = json.load(f)
    f.close()

    address = config['ethereum']['contract_address']

    assert address[0:2] == '0x'
    assert len(address) == 42

    os.chdir('../ethereum')

    eth = bbc_ethereum.BBcEthereum(config['ethereum']['network'],
                                   config['ethereum']['private_key'],
                                   address)

    print("\ncontract has been deployed; setting a value.")
    eth.blockingSet(0x1234)

    assert eth.test(0x1230) == 0
    assert eth.test(0x1234) > 0

    print("value has been set; setting another value.")
    eth.blockingSet(b'\x43\x21')

    assert eth.test(0x4321) > 0
    assert eth.test(b'\x43\x21') > 0

    os.chdir(prevdir)
    print("==> BBcAnchor is deployed and tested.")


# end of tests/test_bbc_ethereum2.py
