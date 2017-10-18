# encoding:utf-8

"""
使用内部DNS服务器获取域名的CNAME记录
作者：程亚楠
时间：2017.8.25
"""

import DNS
import random
import tldextract
from datetime import datetime
from process_data.db_manage import get_col

target_col = 'domain_ttl'
timeout = 10
server = '222.194.15.253'

col = get_col(target_col)

## 全局变量
g_cnames = []
g_cnames_ttl = []
g_ips = []
g_ips_ttl = []


def find_ns(fqdn_domain):
    """
    获取域名的NS名称
    注意：部分是多级NS，所以需要进行两次判断
    """
    ns = []
    domain_len = len(fqdn_domain.split('.'))
    for i in range(0,domain_len):
        req_obj = DNS.Request()
        try:
            answer_obj = req_obj.req(name=fqdn_domain, qtype=DNS.Type.NS, server=server, timeout=timeout)
        except DNS.Error,e:
            print e
            return [],''  # 空ns
        for i in answer_obj.answers:
            if i['typename'] == 'NS':
                ns.append(i['data'])
        if ns:
            return ns,fqdn_domain
        else:
            fqdn_domain = extract_main_domain(fqdn_domain)
            domain_tld = tldextract.extract(fqdn_domain)
            if fqdn_domain == domain_tld.suffix:
                return ns,''

def find_ns_tll(main_domain,ns_name):
    """获取域名NS服务器的默认TTL时间"""
    req_obj = DNS.Request()
    answer_obj = req_obj.req(name=main_domain, qtype=DNS.Type.NS, server=ns_name,timeout=timeout)
    for i in answer_obj.answers:
        if i['typename']=='NS' and i['data'] == ns_name:
            print i
            # return i['ttl']


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


def extract_main_domain(fqdn_domain):
    """
    获取次级域名
    """
    fqdn = fqdn_domain.split('.')
    fqdn.pop(0)
    main_domain = '.'.join(fqdn)
    return main_domain


def fetch_rc_ttl(fqdn_domain):
    """
    递归获取域名的cname、cname_ttl和IP、IP_ttl记录
    """
    print '正在查询的域名：',fqdn_domain
    ns,ns_fqdn_domain = find_ns(fqdn_domain)  # 得到ns列表
    # 若无ns，则停止
    if not ns:
        return


    ns_name = random.choice(ns)   # 随机选择一个ns服务器

    find_ns_tll(ns_fqdn_domain,ns_name)
    ip, ip_ttl, cname, cname_ttl = handle_domain_rc(ns_name, fqdn_domain)  # 得到cname和cname的ttl

    # 若cname不为空，则递归进行cname的dns记录获取
    if cname:
        g_cnames.extend(cname)
        g_cnames_ttl.extend(cname_ttl)
        return fetch_rc_ttl(cname[-1])
    elif ip:
        g_ips.extend(ip)
        g_ips_ttl.extend(ip_ttl)





def main():
    global g_cnames, g_cnames_ttl, g_ips, g_ips_ttl
    g_cnames, g_cnames_ttl, g_ips, g_ips_ttl = [], [], [], []  # 初始化
    check_domain = 'www.dxi5.com'
    ## 提取domain+tld
    domain_tld = tldextract.extract(check_domain)
    if domain_tld.suffix == "":
        return
    else:
        check_domain = domain_tld.domain+'.'+domain_tld.suffix
    fqdn_domain = 'www.' + check_domain  # 全域名
    print '查询的域名：',check_domain   # 在查询的域名
    fetch_rc_ttl(fqdn_domain)
    print g_cnames,g_cnames_ttl
    print g_ips, g_ips_ttl


if __name__ == '__main__':
    main()