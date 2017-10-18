# encoding:utf-8

from cdn_list import CDN_PROVIDER
from reverse_cname import domain2cname


def cdn_finder(host):
    for cdn in CDN_PROVIDER:
        if cdn[0] in host:
            return cdn[1]
    return None


def main():
    cnames = domain2cname('www.taobao.com')

    for host in cnames:
        print cdn_finder(host)

if __name__ == '__main__':
    main()
