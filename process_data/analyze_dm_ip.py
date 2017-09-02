# encoding:utf-8
"""
分析页面所有域名的IP、域名和地理信息
"""
from db_manage import get_col
from collections import Counter,defaultdict
import tldextract

def get_sites_data():
    """
    所有IP的长期探测情况
    """
    col = get_col('domain_ip_loc')
    sites_data = col.find({}).skip(3).limit(1)
    return sites_data


def manage_data(site_data):
    """
    处理数据，包括IP、域名、地理位置
    """
    ip_counter = Counter()  # 域名解析出IP个数分布
    ip_sets = Counter()     # IP出现的频次
    ip_domain_sets = defaultdict(set)   # 相同IP对应的域名情况
    ip_country = Counter()     # 国家分布
    tld_counter = Counter()   # 顶级域名个数

    outer_data = site_data['outer_data']

    for i in outer_data:

        # 顶级域名分布
        ext = tldextract.extract(i['domain'])
        tld_counter[ext.suffix] += 1

        ip_counter[len(i['ip'])] += 1    # 域名解析出IP个数的分布

        for ip in i['ip']:
            ip_sets[ip] += 1  # 各个IP出现的频率
            ip_domain_sets[ip].add(i['domain'])  # IP对应的域名

        for l in i['loc']:
            ip_country[l['coutry']] += 1

            # if l['coutry'].encode('utf-8') == '台湾':
            #     print i

    return ip_counter, ip_sets, ip_domain_sets, ip_country, tld_counter


def show_data(data):

    for i,j in data.most_common():
        print i, j


def main():
    sites_data = get_sites_data()
    for i in sites_data:
        ip_counter, ip_set, ip_domain_sets, ip_country, tld_counter =  manage_data(i)

        show_data(ip_country)

if __name__ == '__main__':
    main()


