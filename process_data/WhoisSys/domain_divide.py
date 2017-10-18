#!/usr/bin/env python
# encoding:utf-8

"""
    域名按首字母划分
======================
    1: S+Q+X
    2: C+V
    3: M+N
    4: A+I
    5: T+H
    6: B+J+O
    7: P+G+OTHER
    8: D+L+NUM
    9: F+W+U+Y+Z
    10: E+R+K
"""
from Database.db_opreation import DataBase
from Database.SQL_generate import SQL_generate
from Setting.static import Static

Static.init()
log_main = Static.LOGGER

def get_domain_file():
    domain_list = []
    f = open("example.txt")
    line = f.readline()
    while line:
        line = str(line).lower().strip()
        domain_list.append(line)
        line = f.readline()
    return domain_list

def domain_divide(domain):
    domain = str(domain).lower()
    if domain.find('x--') != -1:
        return 7
    elif domain[0:1] == 's' or domain[0:1] == 'q' or domain[0:1] == 'x':
        return 1
    elif domain[0:1] == 'c' or domain[0:1] == 'v':
        return 2
    elif domain[0:1] == 'm' or domain[0:1] == 'n':
        return 3
    elif domain[0:1] == 'a' or domain[0:1] == 'i':
        return 4
    elif domain[0:1] == 't' or domain[0:1] == 'h':
        return 5
    elif domain[0:1] == 'b' or domain[0:1] == 'j' or domain[0:1] == 'o':
        return 6
    elif domain[0:1] == 'p' or domain[0:1] == 'g':
        return 7
    elif domain[0:1] == 'd' or domain[0:1] == 'l' or domain[0:1].isdigit():
        return 8
    elif domain[0:1] == 'f' or domain[0:1] == 'w' or domain[0:1] == 'u' or domain[0:1] == 'y' or domain[0:1] == 'z':
        return 9
    elif domain[0:1] == 'e' or domain[0:1] == 'r' or domain[0:1] == 'k':
        return 10
    else:
        return 7

if __name__ == "__main__":
    DB = DataBase()
    SQL = SQL_generate()
    DB.db_connect()
    DB.execute_no_return("""USE {database}""".format(database=str(Static.DATABASE_NAME)))
    domain_list = get_domain_file()
    for i in range(len(domain_list)):
        domain = domain_list[i]
        domain_table = 'domain_'+str(domain_divide(domain))
        sql = SQL.GET_DOMAIN_DIVIDE(domain_table, domain)
        DB.execute(sql)
    DB.db_commit()
    DB.db_close()
