# -*- coding: utf-8 -*-

from typing import Tuple
import requests

import sys
sys.path.extend(["../../../"])
from bbc1.core import bbc_config


class BBcBitcoin:

    def __init__(self, domain_id: bytes, gw_server: str, api_key: str, debug=True):
        self.__domain_id = domain_id.hex()
        self.__api_key = api_key
        self.__gw_server = gw_server
        self.__debug = debug


    def get_server(self) -> str:
        return self.__gw_server

    def register(self, digest: bytes) -> Tuple[bool, str]:
        url = f'{self.__gw_server}/anchors/domains/{self.__domain_id}/digests/{digest.hex()}'
        headers = {'X-API-KEY': self.__api_key}

        if self.__debug:
            print(f"Bitcoin::DEBUG::register::set_url::{url}")
            print(f"Bitcoin::DEBUG::register::set_header::{headers}")

        # register the specified digest
        r = requests.post(url, headers=headers)

        if self.__debug:
            print(f"Bitcoin::DEBUG::register::r.status_code::{r.status_code}")
            print(f"Bitcoin::DEBUG::register::r.json::{r.json()}")

        if r.status_code == 400:
            return (False, "invalid_request")
        if r.status_code == 401:
            return (False, "wrong_credentials")
        if r.status_code != 200:
            return (False, "unexpected_error")

        return True, None

    def verify(self, digest: bytes) -> Tuple[bool, str, str]: # ok, errmsg, txid
        url = f'{self.__gw_server}/anchors/domains/{self.__domain_id}/digests/{digest.hex()}'

        if self.__debug:
            print(f"Bitcoin::DEBUG::verify::set_url::{url}")

        # let API server fetch the latest data from blockchain
        r = requests.patch(url)
        if r.status_code != 204:  # No Content
            return (False, "unexpected_error")

        # get anchor by domain ID and digest
        r = requests.get(url)
        if self.__debug:
            print(f"Bitcoin::DEBUG::verify::r.status_code::{r.status_code}")
            print(f"Bitcoin::DEBUG::verify::r.json::{r.json()}")

        if r.status_code == 400:
            return (False, "invalid_request", "")
        if r.status_code == 404:
            return (False, "anchor_not_found", "")
        if r.status_code != 200:
            return (False, "unexpected_error", "")

        # check anchor data
        a = r.json()
        if a["confirmations"] < 6: # return True with message
            return (True, "not_confirmed_yet", a["btctx"])

        return (True, None, a["btctx"])
