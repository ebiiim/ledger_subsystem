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


def test_balance(default_config):

    assert bbc_ethereum.get_balance(default_config) >= 0

    print("\n==> balance is tested.")


# end of tests/test_bbc_ethereum3.py
