#encoding:utf-8

from db_manage import get_col
from reverse_ip import domain2ip
from ip2location import ip2region
from datetime import datetime


def get_sites_data():
    """
    所有IP的长期探测情况
    """
    col = get_col('visited_domains')
    sites_data = col.find({}).skip(2).limit(2)
    return sites_data


def mange_data(domain):
    """
    处理数据
    :param domain: 域名
    :return:
    """
    ips = domain2ip(domain)
    loc = []
    for i in ips:
        loc.append(ip2region(i))
    return ips, loc


def dm_ip_loc(site_data):

    outer_data = []
    source_domain = site_data['domain']
    insert_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    source_ip, source_loc = mange_data(source_domain)

    for domain in site_data['outer_domains']:
        ip,loc = mange_data(domain)
        outer_data.append(
            {'domain': domain,
             'ip': ip,
             'loc': loc
            })

    return {
        'source_domain': source_domain,
        'source_ip': source_ip,
        'source_loc': source_loc,
        'insert_time': insert_time,
        'outer_data': outer_data
    }


def insert_data(scan_data):
    """
    Insert the scan info of ip into the db
    :param scan_data:
    :return:
    """
    # db = get_db()

    col = get_col('domain_ip_loc')
    col.insert_one(scan_data)


def main():
    sites_data = get_sites_data()
    for i in sites_data:
         insert_data(dm_ip_loc(i))


if __name__ == '__main__':
    main()


