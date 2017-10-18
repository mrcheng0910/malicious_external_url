# encoding:utf-8
"""
获取域名的WHOIS信息
domain
reg_phone
updated_date
reg_email
expiration_date
reg_name
top_whois_server
name_server
creation_date


"""
from WhoisSys.main import main
from db_manage import get_col
from datetime import datetime

source_db_name = 'eds_ultimate'
source_col_name = 'detect_resultsbysoft'

target_db_name = 'eds_last'
target_col_name = 'domain_whois1'


def fetch_mal_domains():
    """
    获取待查询的域名列表
    """
    source_col = get_col(source_col_name,source_db_name)
    mal_domains = source_col.find({'flag': 1}, {'_id': 0, 'domain': 1})
    target_col = get_col(target_col_name, target_db_name)
    exist_mal_domains = target_col.find({},{'_id':0,'domain':1})
    mal_domains_list = [ i['domain'] for i in mal_domains]
    exist_mal_domains_list = [i['domain'] for i in exist_mal_domains]

    return list(set(mal_domains_list)-set(exist_mal_domains_list))


def fetch_dm_whois():
    domains = fetch_mal_domains()
    domain_count = len(domains)
    print domain_count
    interval = 100

    for i in range(0,domain_count,interval):
        d = domains[i:i+interval]

        result = main(d)

        extract_field(result)


def extract_field(result):
    insert_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    col = get_col(target_col_name, target_db_name)
    # print result
    for d in result:
        try:
            domain = d['domain']
            reg_phone = d['reg_phone']
            updated_date = d['updated_date']
            reg_email = d['reg_email']
            expiration_date = d['expiration_date']
            reg_name = d['reg_name']
            top_whois_server = d['top_whois_server']
            name_server = d['name_server']
            creation_date = d['creation_date']
            sec_whois_server = d['sec_whois_server']
            org_name = d['org_name']
            sponsoring_registrar = d['sponsoring_registrar']

            # 域名记录若不存在则插入，存在则不做任何操作
            col.insert(
                {
                    "domain": domain,
                     "reg_phone": reg_phone,
                     'updated_date': updated_date,
                     'reg_email': reg_email,
                     'expiration_date': expiration_date,
                     'reg_name': reg_name,
                     'top_whois_server': top_whois_server,
                     'name_server': name_server,
                     'creation_date': creation_date,
                     'sec_whois_server': sec_whois_server,
                     "record_time": insert_time,    # 文档插入时间
                     "org_name": org_name,
                     "sponsoring_registrar":sponsoring_registrar
                }
            )
        except:
            print "出错"
            continue


if __name__ == '__main__':
    fetch_dm_whois()
