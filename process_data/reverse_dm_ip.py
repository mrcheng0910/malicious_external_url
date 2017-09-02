# encoding:utf-8

"""
获取域名的IP地址以及地理位置，同时更新数据库，更新数据库规则如下：
1）若数据库中无该域名记录，则插入；
2）若数据库中有该域名记录，则与该域名最近一次的更新记录进行比较，若相同则不更新，不同则更新。
"""

import schedule
import time

from db_manage import get_col
from reverse_ip import domain2ip
from ip2location import ip2region
from datetime import datetime


def fetch_mal_domains():
    """
    获取待查询的域名列表
    """
    col = get_col('malicious_domains')
    gamble_domains = col.find({}, {'_id': 0, 'domain': 1})  # 赌博网站
    return [ i['domain'] for i in gamble_domains]


def is_ip_same(ips,original_ips):
    """
    判断IP列表是否相同
    """
    ips.sort()
    original_ips.sort()
    return ips == original_ips


def dm_ip_loc(domain):
    """
    得到域名的IP地址列表和IP的地理位置
    """
    ips = domain2ip(domain)
    loc = []
    for i in ips:
        loc.append(ip2region(i))

    return {
        'domain': domain,
        'ips': ips,
        'geos': loc,
    }


def nonexistent_insert_db(domain_geo):
    """
    该域名若不存在则插入
    """
    insert_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    col = get_col('domain_ip_geo')
    domain = domain_geo['domain']

    # 域名记录若不存在则插入，存在则不做任何操作
    result = col.update(
        {
            "domain": domain,
         },
        {
            '$setOnInsert':
             {
                 "ip_geo":
                 [
                     {
                         "ips": domain_geo['ips'],
                         "geo": domain_geo['geos'],
                         "insert_time": insert_time
                     }

                 ],
                 "record_time": insert_time    # 文档插入时间
              }
         },
        True
    )
    return result['updatedExisting']   # 是否更新返回标记位


def update_time(col,domain,ips,insert_time):
    """
    当与最近一条记录相同时，则只更新时间即可
    """
    cur_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    col.update(
        {'domain': domain,
         'ip_geo.ips': ips,
         'ip_geo.insert_time': insert_time
         },
        {
            '$set':
                {'ip_geo.$.insert_time': cur_time}  # 注意$的使用
        }
    )


def update_data(flag, domain_geo):
    """
    若记录存在，则检查该条记录是否需要进行更新
    """
    if not flag:  # 不存在返回
        print "域名新插入"
        return False

    col = get_col('domain_ip_geo')
    insert_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    domain = domain_geo['domain']
    domain_data = col.find({'domain': domain})
    ips = domain_geo['ips']
    cur_record = list(domain_data)[0]['ip_geo'][-1]
    original_ips, original_insert_time = cur_record['ips'],cur_record['insert_time']

    # 如果两者相同，则返回，不修改
    if is_ip_same(ips, original_ips):
        print "与最近记录一致，更新时间"
        update_time(col,domain,ips,original_insert_time)
        return False

    print "与最近记录不一致，新添加记录"
    col.update(
        {'domain': domain},
        {"$push":
             {"ip_geo":
                  {"ips": ips,
                   "geo": domain_geo['geos'],
                   "insert_time": insert_time
                   }
              }
         }
    )
    return True


def main():
    """
    主函数
    """
    domains = fetch_mal_domains()    # 获取待查询的域名列表
    for d in domains:
        print d
        domain_geo = dm_ip_loc(d)
        insert_flag = nonexistent_insert_db(domain_geo)
        update_data(insert_flag,domain_geo)


if __name__ == '__main__':
    main()
    # schedule.every(12).hours.do(main)  # 12小时循环探测一遍
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)