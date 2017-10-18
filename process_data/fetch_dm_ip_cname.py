# encoding:utf-8

"""
1. 获取域名的IP地址以及地理位置，同时更新数据库，更新数据库规则如下：
    1）若数据库中无该域名记录，则插入；
    2）若数据库中有该域名记录，则与该域名最近一次的更新记录进行比较，若相同则不更新，不同则更新。
2. 获取域名的CNAME，同时更新数据库，规则与上相同

程亚楠
创建：2017.9.8
"""

import schedule
import time
import DNS
from db_manage import get_col
from ip2location import ip2region
from datetime import datetime

source_col = 'malicious_domains'
target_col = 'domain_ip_cname1'


def resolve_domain_record(domain):
    """
    获取解析到的域名ip和cname列表
    """
    cnames = []
    ips = []
    req_obj = DNS.Request()
    try:
        answer_obj = req_obj.req(name=domain, qtype=DNS.Type.A, server="222.194.15.253")
        for i in answer_obj.answers:
            if i['typename'] == 'CNAME':
                cnames.append(i['data'])
            elif i['typename'] == 'A':
                ips.append(i['data'])
    except DNS.Base.DNSError:
        cnames = []
        ips =[]

    return ips, cnames


def fetch_mal_domains():
    """
    获取待查询的域名列表
    """
    col = get_col(source_col)
    gamble_domains = col.find({}, {'_id': 0, 'domain': 1,'typ':1})  # 赌博网站
    return [ (i['domain'],i['typ']) for i in gamble_domains]


def is_same(source_data, target_data):
    """
    判断两个列表是否相同
    """
    return sorted(source_data) == sorted(target_data)


def is_cname_same(cnames, original_cnames):
    """
    判断IP列表是否相同
    """
    cnames.sort()
    original_cnames.sort()
    return cnames == original_cnames


def get_ip_cname(domain):
    """
    得到域名的IP地址列表和IP的地理位置
    """

    ips, cnames = resolve_domain_record(domain)

    geos = []
    for i in ips:
        geos.append(ip2region(i))

    return {
        'domain': domain,
        'ips': ips,
        'cnames': cnames,
        'geos': geos
    }


def nonexistent_insert_db(ip_cname, dm_ty):
    """
    该域名若不存在则插入
    """
    insert_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    col = get_col(target_col)
    domain = ip_cname['domain']

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
                         "cnames": ip_cname['cnames'],
                         "insert_time": insert_time
                     }

                 ],
                 'dm_ip':
                 [
                     {
                         "ips": ip_cname['ips'],
                         "geos":ip_cname['geos'],
                         "insert_time": insert_time
                     }
                 ],
                 "record_time": insert_time,    # 文档插入时间
                "dm_type": dm_ty
              },
         },
        True
    )
    return result['updatedExisting']   # 是否更新返回标记位


def update_time(col, domain, dns_type, insert_time,cur_time):
    """
    当与最近一条记录相同时，则只更新时间即可
    """
    col_filed = ""
    if dns_type == 'CNAME':
        col_filed = 'dm_cname'
    elif dns_type == 'A':
        col_filed='dm_ip'

    col.update(
        {'domain': domain,
         col_filed+'.insert_time': insert_time
         },
        {
            '$set':
                {col_filed+'.$.insert_time': cur_time},  # 注意$的使用

            "$inc":
                {
                    "visit_times": 0.5
                }
        }
    )


def update_data(ip_cname):
    """
    若记录存在，则检查该条记录是否需要进行更新
    """
    cur_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    domain = ip_cname['domain']
    ips = ip_cname['ips']
    geos = ip_cname['geos']
    cnames = ip_cname['cnames']


    col = get_col(target_col)
    domain_data = col.find({'domain': domain})  # 得到数据库中已存的记录信息
    d = list(domain_data)[:]
    original_ip_record = d[0]['dm_ip'][-1]
    original_cname_record = d[0]['dm_cname'][-1]

    original_ips, original_ip_insert_time = original_ip_record['ips'], original_ip_record['insert_time']
    original_cnames, original_cname_insert_time = original_cname_record['cnames'],original_cname_record['insert_time']

    # 判断IP是否相同
    if is_same(ips, original_ips):
        print "与最近IP记录一致，更新时间"
        update_time(col, domain, 'A', original_ip_insert_time, cur_time)
    else:
        print "与最近IP记录不一致，新添加记录"
        insert_record(col,"A",domain,ips,cur_time,geos)

    # 判断cname是否相同
    if is_same(cnames, original_cnames):
        print "与最近CNME记录一致，更新时间"
        update_time(col,domain,'CNAME',original_cname_insert_time,cur_time)
    else:
        print "与最近CNAME记录不一致，新添加记录"
        insert_record(col,'CNAME',domain,cnames,cur_time,geos)


def insert_record(col,dns_type,domain,insert_data,cur_time,geos):
    name_field = {}

    if dns_type == "CNAME":
        name_field = {
            "dm_cname":{
                "cnames": insert_data,
                "insert_time": cur_time
            }
        }
    elif dns_type == "A":
        name_field = {
            "dm_ip":{
                "ips":insert_data,
                "geos":geos,
                "insert_time": cur_time
            }
        }

    col.update(
        {'domain': domain},
        {"$push": name_field,
         "$inc":
             {
                 "visit_times": 0.5
             }
         }
    )


def main():
    """
    主函数
    """
    domains = fetch_mal_domains()    # 获取待查询的域名列表
    for d, dm_ty in domains:
        print d, ':', dm_ty
        try:
            ip_cname = get_ip_cname('www.'+d)   # 注意添加www
            insert_flag = nonexistent_insert_db(ip_cname,dm_ty)
            if insert_flag:
                update_data(ip_cname)
            else:
                print "域名新插入"
        except:
            print "异常"
            continue


if __name__ == '__main__':
    main()
    schedule.every(2).hours.do(main)  # 12小时循环探测一遍
    while True:
        schedule.run_pending()
        time.sleep(1)