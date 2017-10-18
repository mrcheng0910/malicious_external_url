# encoding:utf-8

"""
使用内部DNS服务器获取域名的ns服务器和其ttl时间
作者：程亚楠
时间：2017.10.18
注意事项：
因为部分域名的zone文件配置错误，导致无法获取ns服务器，但是其可正常解析，例如dxi5.com

"""

import DNS
import random
import tldextract
from datetime import datetime
from process_data.db_manage import get_col

target_col = 'domain_ns_ttl'
timeout = 5
server = '222.194.15.253'

col = get_col(target_col)

def fetch_mal_domains():
    """
    获取待查询的域名和恶意类型
    """
    col = get_col("malicious_domains")
    mal_domains = col.find({}, {'_id': 0, 'domain': 1,'typ':1})
    return [ (i['domain'],i['typ']) for i in mal_domains]


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
            print '获取NS服务器异常：', e
            return [], ''  # 空ns
        for i in answer_obj.answers:
            if i['typename'] == 'NS':
                ns.append(i['data'])
        if ns:
            return ns,fqdn_domain
        else:
            fqdn_domain = extract_main_domain(fqdn_domain)
            domain_tld = tldextract.extract(fqdn_domain)
            if fqdn_domain == domain_tld.suffix:
                return [], ''


def find_ns_tll(main_domain,ns_name):
    """获取域名NS服务器的默认TTL时间"""
    ns = []
    ns_ttl = []
    req_obj = DNS.Request()
    try:
        answer_obj = req_obj.req(name=main_domain, qtype=DNS.Type.NS, server=ns_name,timeout=timeout)
    except DNS.Error,e:
        print '获取ns的ttl时间异常：', e
        return [],[]

    for i in answer_obj.answers:
        if i['typename']=='NS':
            ns.append(i['data'])
            ns_ttl.append(i['ttl'])
    return ns,ns_ttl

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
    递归获取域名的ns和ns_ttl记录
    """
    ns, ns_fqdn_domain = find_ns(fqdn_domain)  # 得到ns列表
    # 若无ns，则停止
    if not ns:
        print '异常：未获取NS服务器'
        return [],[]
    ns_name = random.choice(ns)   # 随机选择一个ns服务器
    ns, ns_ttl = find_ns_tll(ns_fqdn_domain,ns_name)
    return ns, ns_ttl


def insert_data(check_domain,ns,ns_ttl,mal_type):
    """
    更新数据库
    """
    insert_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ## 若无该域名数据，则插入到数据库中
    result = col.update(
        {
            "domain": check_domain,
            "mal_type": mal_type,
        },
        {
            "$setOnInsert": {
                'data': [
                    {

                        "ns": ns,
                        "ns_ttl": ns_ttl,
                        'insert_time': insert_time
                    }
                ]
            }
        },
        True
    )
    rc_data = {
        'data':
            {
                "ns": ns,
                "ns_ttl": ns_ttl,
                'insert_time': insert_time
            }
    }
    # print result['updatedExisting']  # 是否更新返回标记位,True表示存在，False表示不存在
    ## 若已有该域名数据，则添加字段
    if result['updatedExisting']:
        col.update(
            {'domain': check_domain},
            {"$push": rc_data}
        )


def main():

    mal_domain = fetch_mal_domains()

    for check_domain, domain_type in mal_domain[:10]:
        ## 提取domain+tld
        domain_tld = tldextract.extract(check_domain)
        if domain_tld.suffix == "":
            continue
        else:
            check_domain = domain_tld.domain+'.'+domain_tld.suffix
        fqdn_domain = 'www.' + check_domain  # 全域名
        print '查询的域名：',check_domain   # 在查询的域名
        ns, ns_ttl = fetch_rc_ttl(fqdn_domain)
        print ns,ns_ttl
        insert_data(check_domain,ns,ns_ttl,domain_type)


if __name__ == '__main__':
    main()