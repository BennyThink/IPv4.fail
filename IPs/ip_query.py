# coding: utf-8
# IPv4.fail - ip_query.py
# 2019/5/13 14:31

__author__ = 'Benny <benny@bennythink.com>'

from IPs.ipv4 import query_ipv4
from IPs.ipv6 import query_ipv6


def simple_query(ip: str) -> str:
    if ":" in ip:
        return query_ipv6(ip)
    else:
        return query_ipv4(ip)


if __name__ == '__main__':
    print(simple_query('54.222.60.252'))
    print(simple_query('2603:c020:1:d5ff:81b6:76d6:60fd:cb51'))
