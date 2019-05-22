# -*- coding: utf-8 -*-
from brownie import *
import scripts.bbc_anchor


def setup():
    scripts.bbc_anchor.main()


def test_my_anchor():

    digest0 = 0x000102030405060708090a0b0c0d0e0f000102030405060708090a0b0c0d0e0f
    digest1 = 0x800102030405060708090a0b0c0d0e0f000102030405060708090a0b0c0d0e0f

    anchor = BBcAnchor[0]

    check.true(anchor.isStored(digest0) == False)
    check.true(anchor.getStored(digest0) == 0)

    anchor.store(digest0, {'from': accounts[0]})

    check.true(anchor.isStored(digest0) == True)
    check.true(anchor.getStored(digest0) > 0)

    check.true(anchor.isStored(digest1) == False)

    anchor.store(digest1, {'from': accounts[0]})

    check.true(anchor.isStored(digest1) == True)


# end of test_bbc_anchor.py
