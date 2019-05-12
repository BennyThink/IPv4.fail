# coding: utf-8
# IPv4.fail - ipv4.py
# 2019/5/12 12:55

__author__ = 'Benny <benny@bennythink.com>'

import ipdb

db = ipdb.City("ip_database/ipv4_ipip.ipdb")
# db.reload("/path/to/city.ipv4.ipdb") # update ipdb database file reload data
# print(db.is_ipv4(), db.is_ipv6())
print(db.languages())  # support language

print(db.find("www.baidu.com", "CN"))  # Python 2.7
print(db.find_map("123.185.180.106", "CN"))  # query ip return dict
print(db.find_info("118.28.1.1", "CN").country_name)
