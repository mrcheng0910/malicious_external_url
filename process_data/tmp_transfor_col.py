# encoding:utf-8

"""
使用内部DNS服务器获取域名IP、CNAME、NS和对应的TTL时间
从根域名向下进行查询
作者：程亚楠
时间：2017.8.25
"""

import DNS
import random
import tldextract
from datetime import datetime
from db_manage import get_col
from pandas import Series

timeout = 5   # 超时时间
# server = '222.194.15.253'
target_col = 'white_dns_ttl_top'
col = get_col(target_col)

def fetch_mal_domains():
    """
    获取待查询的域名列表
    """
    col = get_col('domain_ttl_white_new')
    mal_domains = col.find({})  # 赌博网站
    print mal_domains.count()
    for i in mal_domains:
        insert_data(i['domain'],i['data'][0]['cnames'],i['data'][0]['cnames_ttl'],i['data'][0]['ips'],i['data'][0]['ips_ttl'],i['data'][0]['ns'],i['data'][0]['ns_ttl'],i['mal_type'])


def insert_data(check_domain,cnames,cnames_ttl,ips,ips_ttl,ns,ns_ttl,mal_type):
    insert_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = col.update(
        {
            "domain": check_domain,
        },
        {
            "$setOnInsert": {
                "mal_type": mal_type,
                "cnames": cnames,
                "cnames_ttl": cnames_ttl,
                'ips': ips,
                'ips_ttl': ips_ttl,
                'ns':ns,
                'ns_ttl':ns_ttl,
                'insert_time': insert_time
            }
        },
        True
    )







def main():
    fetch_mal_domains()

if __name__ == '__main__':
    main()