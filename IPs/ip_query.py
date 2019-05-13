# coding: utf-8
# IPv4.fail - ip_query.py
# 2019/5/13 14:31

__author__ = 'Benny <benny@bennythink.com>'


import ipdb
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'ip_database')


def simple_query(ip: str) -> str:
    # TODO: non-Chinese IP may need to query maxmind.
    if ':' in ip:
        # IPv6
        pass
    else:
        db = ipdb.City(os.path.join(DB_PATH, "ipv4_ipip.ipdb"))
        return ' '.join(db.find(ip, "CN"))


if __name__ == '__main__':
    print(simple_query('1.1.1.1'))
