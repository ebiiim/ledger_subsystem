# -*- coding: utf-8 -*-
import pytest
from brownie import *
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


def test_setup_brownie(default_config):

    bbc_ethereum.setup_brownie(default_config, TEST_INFURA_PROJECT_ID)

    prevdir = os.getcwd()
    os.chdir(bbc1.__path__[0] + '/core/' + bbc_config.DEFAULT_WORKING_DIR)

    f = open(TEST_CONFIG_FILE, 'r')
    config = json.load(f)
    f.close()

    infura_project_id = config['ethereum']['web3_infura_project_id']

    assert infura_project_id == TEST_INFURA_PROJECT_ID

    os.chdir(prevdir)
    print("\n==> brownie is set up.")


def test_setup_new_account(default_config):

    if TEST_INFURA_PROJECT_ID == '':
        return

    bbc_ethereum.setup_new_account(default_config)

    prevdir = os.getcwd()
    os.chdir(bbc1.__path__[0] + '/core/' + bbc_config.DEFAULT_WORKING_DIR)

    f = open(TEST_CONFIG_FILE, 'r')
    config = json.load(f)
    f.close()

    private_key = config['ethereum']['private_key']

    assert private_key[0:2] == '0x'

    accounts[0].private_key == private_key

    os.chdir(prevdir)
    print("\n==> new account is set.")


# end of tests/test_bbc_ethereum1.py
