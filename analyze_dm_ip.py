#encoding:utf-8

from db_manage import get_col

from collections import Counter

def get_sites_data():
    """
    所有IP的长期探测情况
    """
    col = get_col('domain_ip_loc')
    sites_data = col.find({})
    return sites_data


def cal_ip_count(site_data):

    ip_counter = Counter()
    outer_data = site_data['outer_data']

    for i in outer_data:
        ip_counter[len(i['ip'])] += 1

        # if len(i['ip']) == 3:
        #     print i


    print ip_counter







def main():
    sites_data = get_sites_data()
    for i in sites_data:
        cal_ip_count(i)


if __name__ == '__main__':
    main()


