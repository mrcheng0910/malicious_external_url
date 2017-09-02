#encoding:utf-8

from db_manage import get_col
from reverse_ip import domain2ip
from ip2location import ip2region
from datetime import datetime
import tldextract

def get_sites_data():
    """
    所有IP的长期探测情况
    """
    col = get_col('visited_domains')

    sites_data = col.find({}).skip(3).limit(1)
    return sites_data

def analyze_links(site_data):

    external_links_domains = set()
    internal_count = len(site_data['inter_urls'])
    external_count = len(site_data['outer_urls'])

    external_domains = [ d for d in site_data['outer_domains']]


    for url in site_data['outer_urls']:
        ext = tldextract.extract(url)
        external_links_domains.add(ext.domain+'.'+ext.suffix)

    print internal_count
    print external_count
    print len(external_links_domains)
    print len(external_domains)
    print len(set(external_domains)-external_links_domains)




if __name__ == '__main__':

    sites_data = get_sites_data()

    for i in sites_data:
        analyze_links(i)







