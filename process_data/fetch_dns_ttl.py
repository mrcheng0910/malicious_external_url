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
target_col = 'domain_ttl_new'
col = get_col(target_col)

## 全局变量
g_cnames = []
g_cnames_ttl = []
g_ips = []
g_ips_ttl = []
g_ns = []
g_ns_ttl = []


def fetch_domain_ns(domain,server = '222.194.15.253'):
    """
    获取域名的NS记录
    """
    ns,ns_ttl,qry_result = [],[],[]
    req_obj = DNS.Request()
    try:
        answer_obj = req_obj.req(name=domain, qtype=DNS.Type.NS, server=server, timeout=timeout)
    except DNS.Error,e:
        print e
        return [],[]  # 空ns
    if answer_obj.answers:
        qry_result = answer_obj.answers
    elif answer_obj.authority:
        qry_result = answer_obj.authority
    for i in qry_result:
        if i['typename'] == 'NS':
            ns.append(i['data'])
            ns_ttl.append(i['ttl'])
    return ns, ns_ttl


def manage_ns(fqdn_domain):
    """
    获取查询域名的NS记录
    :param fqdn_domain:
    """
    domain_tld = tldextract.extract(fqdn_domain)
    tld_ns,tld_ns_ttl = fetch_domain_ns(domain_tld.suffix)
    if not tld_ns:
        return [],[]
    domain_ns,domain_ns_ttl = fetch_domain_ns(domain_tld.domain+'.'+domain_tld.suffix,random.choice(tld_ns))
    if domain_ns:
        fqdn_domain_ns,fqdn_domain_ns_ttl = fetch_domain_ns(fqdn_domain,random.choice(domain_ns))
        if fqdn_domain_ns:
            return fqdn_domain_ns,fqdn_domain_ns_ttl
        else:
            return domain_ns,domain_ns_ttl
    else:
        fqdn_domain_ns,fqdn_domain_ns_ttl = fetch_domain_ns(fqdn_domain)
        return fqdn_domain_ns,fqdn_domain_ns_ttl


def handle_domain_rc(ns_name,domain):
    """
    获取指定dns记录的内容和ttl时间，主要为A记录和CNAME记录
    """
    ip,ip_ttl,cname,cname_ttl = [],[],[],[]
    req_obj = DNS.Request()
    try:
        answer_obj = req_obj.req(name=domain, qtype=DNS.Type.A, server=ns_name, timeout=timeout)
    except DNS.Error, e:
        print '获取域名记录：', e
        return [], [],[],[]

    for i in answer_obj.answers:
        r_data = i['data']
        r_ttl = i['ttl']
        if i['typename'] == 'A':
            ip.append(r_data)
            ip_ttl.append(r_ttl)
        elif i['typename'] == 'CNAME':
            cname.append(r_data)
            cname_ttl.append(r_ttl)

    return ip, ip_ttl, cname, cname_ttl


def fetch_rc_ttl(fqdn_domain,original_domain):
    """
    递归获取域名的cname、cname_ttl和IP、IP_ttl记录
    """
    ns,ns_ttl = manage_ns(fqdn_domain)  # 得到ns列表
    # 若无ns，则停止
    if not ns:
        return
    if fqdn_domain == original_domain:
        g_ns.extend(ns)
        g_ns_ttl.extend(ns_ttl)
    ns_name = random.choice(ns)   # 随机选择一个ns服务器
    ip, ip_ttl, cname, cname_ttl = handle_domain_rc(ns_name, fqdn_domain)  # 得到cname和cname的ttl

    # 若cname不为空，则递归进行cname的dns记录获取
    if cname:
        g_cnames.extend(cname)
        g_cnames_ttl.extend(cname_ttl)
        return fetch_rc_ttl(cname[-1],original_domain)
    elif ip:
        g_ips.extend(ip)
        g_ips_ttl.extend(ip_ttl)


def insert_data(check_domain,cnames,cnames_ttl,ips,ips_ttl,ns,ns_ttl,mal_type):
    """
    插入数据
    """
    insert_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rc_data = {
        'domain': check_domain,
        'mal_type': mal_type,
        'data':
            {
                "cnames": cnames,
                "cnames_ttl": cnames_ttl,
                'ips': ips,
                'ips_ttl': ips_ttl,
                "ns":ns,
                "ns_ttl":ns_ttl,
                'insert_time': insert_time
            }
    }
    col.insert(rc_data)


def fetch_mal_domains():
    """
    获取待查询的域名列表
    """
    col = get_col(target_col)
    mal_domains = col.find({}, {'_id': 0, 'domain': 1,'typ':1})  # 赌博网站
    return [ i['domain'] for i in mal_domains]


def fetch_mal_domains_from_file():
    """
    从文件中获取待查询的域名数据
    """
    mal_domains = []
    mal_type = []
    fp = open('mal_domains.txt','r')
    db_mal_domains = fetch_mal_domains()
    fp_lines = fp.readlines()
    for i in fp_lines:
        domain_type = i.strip().split('\t')
        mal_domains.append(domain_type[0])
        mal_type.append(domain_type[1])

    domain_series = Series(mal_type,index=mal_domains)
    un_detected_domains = list(set(mal_domains)-set(db_mal_domains))
    domain_series = domain_series[un_detected_domains]
    return domain_series


def main():

    global g_cnames, g_cnames_ttl, g_ips, g_ips_ttl,g_ns,g_ns_ttl
    mal_domains = fetch_mal_domains_from_file()
    domain_total = mal_domains.size

    for check_domain,mal_type in mal_domains.iteritems():
        print domain_total
        domain_total -= 1
        g_cnames, g_cnames_ttl, g_ips, g_ips_ttl,g_ns,g_ns_ttl = [], [], [], [],[],[]  # 初始化

        ## 提取domain+tld
        domain_tld = tldextract.extract(check_domain)
        if domain_tld.suffix == "":
            continue
        else:
            check_domain = domain_tld.domain+'.'+domain_tld.suffix
        fqdn_domain = 'www.' + check_domain  # 全域名
        print '查询的域名：',check_domain   # 在查询的域名
        fetch_rc_ttl(fqdn_domain,fqdn_domain)
        print g_cnames,g_cnames_ttl
        print g_ips, g_ips_ttl
        print g_ns,g_ns_ttl
        insert_data(check_domain,g_cnames,g_cnames_ttl,g_ips,g_ips_ttl,g_ns,g_ns_ttl,mal_type)


if __name__ == '__main__':

    main()
    # fetch_mal_domains_from_file()