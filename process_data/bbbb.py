# encoding:utf-8

"""
获取域名的IP地址以及地理位置，同时更新数据库，更新数据库规则如下：
1）若数据库中无该域名记录，则插入；
2）若数据库中有该域名记录，则与该域名最近一次的更新记录进行比较，若相同则不更新，不同则更新。
"""

import schedule
import time

from db_manage import get_col
from aaaaaa import domain2cname
from datetime import datetime

source_col = 'malicious_domains'
target_col = 'domain_cname1'


def fetch_mal_domains():
    """
    获取待查询的域名列表
    """
    col = get_col(source_col)
    gamble_domains = col.find({}, {'_id': 0, 'domain': 1,'typ':1})  # 赌博网站
    return [ (i['domain'],i['typ']) for i in gamble_domains]


def is_cname_same(cnames, original_cnames):
    """
    判断IP列表是否相同
    """
    cnames.sort()
    original_cnames.sort()
    return cnames == original_cnames


def fetch_dm_cname(domain):
    """
    得到域名的IP地址列表和IP的地理位置
    """

    cnames, ttls = domain2cname(domain)
    return {
        'domain': domain,
        'cnames': cnames,
        'ttls': ttls
    }


def nonexistent_insert_db(domain_cname, dm_ty):
    """
    该域名若不存在则插入
    """
    insert_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    col = get_col(target_col)
    domain = domain_cname['domain']

    # 域名记录若不存在则插入，存在则不做任何操作
    result = col.update(
        {
            "domain": domain,
         },
        {
            "$setOnInsert":
             {
                 "dm_cname":
                 [
                     {
                         "cnames": domain_cname['cnames'],
                         'ttls': domain_cname['ttls'],
                         "insert_time": insert_time
                     }

                 ],
                 "record_time": insert_time,    # 文档插入时间
                "dm_type":dm_ty
              },
         },
        True
    )
    return result['updatedExisting']   # 是否更新返回标记位


def update_time(col, domain, cnames, insert_time):
    """
    当与最近一条记录相同时，则只更新时间即可
    """
    cur_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    col.update(
        {'domain': domain,
         # 'dm_cname.cnames': cnames,
         'dm_cname.insert_time': insert_time
         },
        {
            '$set':
                {'dm_cname.$.insert_time': cur_time},  # 注意$的使用

            "$inc":
                {
                    "visit_times": 1
                }
        }
    )


def update_data(flag, domain_cname):
    """
    若记录存在，则检查该条记录是否需要进行更新
    """
    if not flag:  # 不存在返回
        print "域名新插入"
        return False

    col = get_col(target_col)
    insert_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    domain = domain_cname['domain']
    domain_data = col.find({'domain': domain})
    cnames = domain_cname['cnames']
    ttls = domain_cname['ttls']
    cur_record = list(domain_data)[0]['dm_cname'][-1]
    original_cnames, original_insert_time = cur_record['cnames'],cur_record['insert_time']

    # 如果两者相同，则返回，不修改
    if is_cname_same(cnames, original_cnames):
        print "与最近记录一致，更新时间"
        update_time(col,domain,cnames,original_insert_time)
        return False

    print "与最近记录不一致，新添加记录"
    col.update(
        {'domain': domain},
        {"$push":
             {
                 "dm_cname":
                      {"cnames": cnames,
                       "ttls": ttls,
                       "insert_time": insert_time
                       }
              },
         "$inc":
             {
                 "visit_times": 1
             }
         }
    )
    return True


def main():
    """
    主函数
    """
    domains = fetch_mal_domains()    # 获取待查询的域名列表
    for d, dm_ty in domains:
        print d, ':', dm_ty
        # try:
        cnames = fetch_dm_cname(d)
        insert_flag = nonexistent_insert_db(cnames,dm_ty)
        update_data(insert_flag,cnames)
        # except:
        #     print "异常"
        #     continue


if __name__ == '__main__':
    main()
    # schedule.every(2).hours.do(main)  # 12小时循环探测一遍
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)