#!/usr/bin/env python
# encoding:utf-8

"""
    主流程-程序入口
=====================

version   :   1.0
author    :   @`13
time      :   2017.2.11
"""


import Queue
import threading
from time import sleep

from Database.db_opreation import DataBase  # 数据库对象
from Database.update_record import WhoisRecord  # 更新信息函数
from get_domain_whois import get_domain_whois  # 获取whois函数
from Setting.static import Static  # 静态变量,设置






def GetWhois():
    """获取whois,并放入Whois队列中"""
    global DomainQueue, WhoisQueue
    while not DomainQueue.empty():
        domain= DomainQueue.get()
        result = get_domain_whois(domain)
        print result
        if result:
            WhoisQueue.put(result)
        if Ban_Setting:
            sleep(0.1)  # 防ban
    return



def WriteWhoisInfo(DataBaseObject):
    """更新whois数据到数据库中"""
    global DomainQueue, WhoisQueue
    global whois_result_dict
    WhoisInfoDict = WhoisRecord(DataBaseObject)
    while not (WhoisQueue.empty() and DomainQueue.empty()):  # 当双队列不空时候:
        if not WhoisQueue.empty():
            whois_dict = WhoisQueue.get()
            #WhoisInfoDict.Update(whois_dict, old_flag)
            whois_result_dict.append(whois_dict)
        else:
            sleep(0.5)

def main(domain_list):
    """
    主流程函数,获取whois并更新到数据库中
    :param Worktype: 工作方式  0 - 获取新增域名
                              1 - 重新获取所有域名数据
                             -1 - 获取失败域名
                            SQL - 特定获取域名的SQL语句
    """
    Static.init()
    log_main = Static.LOGGER

    # 全局变量声明
    global whois_result_dict
    whois_result_dict = []

    global DomainQueue, WhoisQueue
    DomainQueue = Queue.Queue()  # 任务域名队列
    WhoisQueue = Queue.Queue()  # whois结果队列

    global Process_Num, Ban_Setting
    Process_Num = Static.PROCESS_NUM  # 获取进程数
    Ban_Setting = False  # 防Ban设置
    # 初始化操作对象
    DB = DataBase()
    DB.db_connect()
    # 填充域名队列
    for domain in domain_list:
        # print domain
        DomainQueue.put(str(domain).strip())
    # 开始多线程获取域名
    thread_list = []
    for i in range(Process_Num):
        get_whois_thread = threading.Thread(target=GetWhois)
        get_whois_thread.setDaemon(True)
        get_whois_thread.start()
        thread_list.append(get_whois_thread)
    # 开始域名字典,更新数据库
    sleep(Static.SOCKS_TIMEOUT)  # 等待队列填充
    update_whois_thread = threading.Thread(target=WriteWhoisInfo(DB))
    update_whois_thread.setDaemon(True)
    update_whois_thread.start()
    thread_list.append(update_whois_thread)
    # 挂起进程直到结束
    for update_whois_thread in thread_list:
        update_whois_thread.join()
    log_main.error("结束")
    # 清空队列
    while not WhoisQueue.empty():
        whois_result_dict.append(WhoisQueue.get())
    while not DomainQueue.empty():
        DomainQueue.get()
    DB.db_commit()
    DB.db_close()
    return whois_result_dict


# if __name__ == '__main__':
#     print "whois探测开始"
#     domain_list = ['sina.com']
#     result = main(domain_list)
# #
#     print result