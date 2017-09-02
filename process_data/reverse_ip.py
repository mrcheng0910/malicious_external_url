# encoding:utf-8

"""
使用内部DNS服务器获取域名的IP地址
作者：程亚楠
时间：2017.8.25
"""

import dns.resolver


def domain2ip(domain):
    """
    获取解析到的域名IP列表
    参数
        domain: string 待解析的域名

    返回值
        ips: list 域名解析后的ip列表
    """

    ips = []
    res = dns.resolver.Resolver()
    # 防止dns服务器拒绝服务，使用多个dns服务器
    res.nameservers = ['8.8.8.8', '8.8.4.4', '114.114.114.114', '223.5.5.5','223.6.6.6']
    res.nameservers = ['222.194.15.253']

    try:
        domain_ip = res.query(domain, 'A')
        for i in domain_ip:
            ips.append(i.address)
    except:
        ips = []
    return ips