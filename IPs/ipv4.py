#!/usr/bin/env python3
# coding: utf-8

# IPv4.fail - ipv4.py
# 2023-02-11  14:37


import pathlib

import ipdb

DB_PATH = pathlib.Path(__file__).parent / 'data' / 'ipip.net.ipdb'


def is_china_ip(ipv4):
    pass


def query_ipv4(ipv4):
    db = ipdb.City(DB_PATH)
    return ' '.join(db.find(ipv4, "CN"))
