# encoding:utf-8

"""
使用内部DNS服务器获取域名的CNAME记录
作者：程亚楠
时间：2017.8.25
"""

import DNS


def domain2cname(domain):
    """
    获取解析到的域名cname列表
    """
    cnames = []
    reqobj = DNS.Request()
    try:
        answerobj_a = reqobj.req(name=domain, qtype=DNS.Type.A, server="222.194.15.253")

        for i in answerobj_a.answers:
            if i['typename'] == 'CNAME':
                cnames.append(i['data'])
    except DNS.Base.DNSError:
        cnames = []

    return cnames



def domain2ip(domain):
    """
    获取解析到的域名cname列表
    """
    ips = []
    reqobj = DNS.Request()
    try:
        answerobj_a = reqobj.req(name=domain, qtype=DNS.Type.A, server="222.194.15.253")
        # answerobj_a = reqobj.req(name=domain, qtype=DNS.Type.NS, server="114.114.114.114")
        # answerobj_a = reqobj.req(name=domain, qtype=DNS.Type.NS, server="8.8.8.8")
        # answerobj_a = reqobj.req(name=domain, qtype=DNS.Type.A, server="f.gtld-servers.net")


        for i in answerobj_a.answers:
            print i
            # if i['typename'] == 'A':
            #     ips.append(i['data'])
    except DNS.Base.DNSError:
        ips = []

    return ips

def find_ns(domain):
    reqobj = DNS.Request()
    answerobj_a = reqobj.req(name=domain, qtype=DNS.Type.NS,server="222.194.15.253")
    print answerobj_a
    for i in answerobj_a.answers:
        print i

# print "ndlkdjl"
domain = 'baidu.com'
# find_ns(domain)
domain2ip('www.ifeng.com')


# domains= ['baidu.com']
# domains = ['www.ifeng.com.lxdns.com']
# domains = ['www.ifeng.com.ifengcdn.com']
# for i in domains:
#     print domain2ip(i)
#
# print domain2cname('www.chinadaily.com.cn')
# print domain2cname('www.ifeng.com')
