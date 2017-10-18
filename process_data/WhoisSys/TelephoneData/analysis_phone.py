#!/usr/bin/env python
# encoding:utf-8

import  MySQLdb
import sys

reload(sys)
sys.setdefaultencoding('utf8')

class Analysis_tel(object):
    def __init__(self,result):
        self.conn2 = MySQLdb.connect(host="172.29.152.249", user="root", passwd="platform", db="location",charset='utf8')
        self.cursor2 = self.conn2.cursor()
        self.result = result

    def analysis(self,sql):
        global flag_all
        global flag_25
        global province
        global city
        self.cursor2.execute(sql)
        results_2 = self.cursor2.fetchall()
        if (results_2):
            flag_all=1
            flag_25=1
            for row2 in results_2:
                province = row2[2].encode('utf-8')
                city = row2[3].encode('utf-8')
                self.result['province'] = province
                self.result['city'] = city
    def up(self,ponum,number,type):
        self.result['posi_n'] = ponum
        self.result['type'] = type
        self.result['nu_n'] = number

    def up_type(self,type):
        self.result['type'] = type

    def analysis_special(self,number):
        global flag_all
        n = len(number)
        i1 = number[0]  # 每位都重复
        i2 = number[0:2]  # 两位一重复
        i3 = number[0:3]  # 三位一重复
        i4 = "12345"
        if ((number.count(i1) == n or number.count(i2) == n/2 or number.count(i4)==1) or (number.count(i3)==n/3 and len(number)>=6)):  # 有一定重复规律的号段可能是假的，置为25（第二种类型的5错误）
            type = "25"
            flag_all=1
            Analysis_tel.up_type(self,type)

    def analysis_phone(self):
        try:
            global flag_all
            global flag_25
            global province
            global city
            flag_all = 0
            flag_25=0
            province=""
            city=""
            number = self.result['nu_n']
            type = self.result['ty_n']
            if number:
                Analysis_tel.analysis_special(self,number)
                if (flag_all == 0):  # 不在异常电话范围内
                    if (type == "02"):  # 总共12位，可能是手机号前加了0
                        if (number[0] == "1" and number[1]!="0"):  # 可能是标准11位手机，不改type
                            phone_pre = number[0:7]
                            sql2 = "SELECT * FROM phone_china2 WHERE phone = '%s'" % (phone_pre)  # 根据索引直接去数据源表中相关地址查询省份和城市
                            Analysis_tel.analysis(self,sql2)
                            if(flag_all==0):#标准11位手机格式但解析不了，置为020
                                Analysis_tel.up_type(self,"020")

                        elif (number[0] == "0"):  # 可能是11位标准固话
                            quhao1 = number[0:3]
                            quhao2 = number[0:4]
                            sql2 = "SELECT * FROM telphone WHERE quhao = '%s'" % (quhao1)  # 根据索引直接去数据源表中相关地址查询省份和城市
                            Analysis_tel.analysis(self,sql2)
                            if(flag_all==1):#02类型去0之后可以解析成固话的，置为021
                                ponum="0"+quhao1
                                number_new=number[3:]
                                Analysis_tel.up(self,ponum,number_new,"021")
                            else:
                                sql3 = "SELECT * FROM telphone WHERE quhao = '%s'" % (quhao2)  # 根据索引直接去数据源表中相关地址查询省份和城市
                                Analysis_tel.analysis(self,sql3)
                                if(flag_all==1):
                                    ponum="0"+quhao2
                                    number_new=number[4:]
                                    Analysis_tel.up(self,ponum,number_new,"021")
                                else:#11位固话形式的，但是无法解析，置为0210
                                    Analysis_tel.up_type(self,"0210")
                        else:
                            Analysis_tel.up_type(self,"0200")

                    elif (type == "0" or type=="03"):  # 标准11位手机号
                        phone_pre = number[0:7]
                        sql2 = "SELECT * FROM phone_china2 WHERE phone = '%s'" % (phone_pre)  # 根据索引直接去数据源表中相关地址查询省份和城市
                        Analysis_tel.analysis(self,sql2)
                        if(flag_all==0):
                            if(type=="0"):#标准11位手机格式无法解析的，置为00
                                Analysis_tel.up_type(self,"00")
                            elif(type=="03"):#非标准位数的手机格式无法解析的，置为030
                                Analysis_tel.up_type(self,"030")

                    elif (type == "1" or type == "12" or type=="14"):  # 可以解析得了的固话
                        quhao = self.result['posi_n']
                        sql2 = "SELECT * FROM telphone WHERE quhao = '%s'" % (quhao)  # 根据索引直接去数据源表中相关地址查询省份和城市
                        Analysis_tel.analysis(self,sql2)
                    elif (type == "11" or type == "13"):  # 固话前少了0
                        quhao = "0" + self.result['posi_n']
                        print quhao
                        sql2 = "SELECT * FROM telphone WHERE quhao = '%s'" % (quhao)  # 根据索引直接去数据源表中相关地址查询省份和城市
                        Analysis_tel.analysis(self,sql2)
                        print self.result
                else:#在电话异常范围内
                    if self.result['posi_n']:
                        quhao=self.result['posi_n']
                        sql2 = "SELECT * FROM telphone WHERE quhao = '%s'" % (quhao)  # 根据索引直接去数据源表中相关地址查询省份和城市
                        Analysis_tel.analysis(self,sql2)
                        if(flag_25==1):#25错误类型可以解析成固话的，置为251
                            Analysis_tel.up_type(self,"251")
                        else:
                            quhao="0"+self.result['posi_n']
                            sql2 = "SELECT * FROM telphone WHERE quhao = '%s'" % (quhao)  # 根据索引直接去数据源表中相关地址查询省份和城市
                            Analysis_tel.analysis(self,sql2)
                            if (flag_all == 1):  # 25错误类型可以解析成固话的，置为251
                                Analysis_tel.up_type(self,"251")
            self.conn2.commit()
        except Exception,e:
            print e
            print "error"

    def analysistel(self):
        Analysis_tel.analysis_phone(self)
        self.conn2.close()
        return self.result

if __name__ == "__main__":
    result = {'province': '', 'city': '', 'country': '\xe4\xb8\xad\xe5\x9b\xbd', 'posi_n': '10', 'nu_n': '5985888', 'country_n': '+86', 'ty_n': '11'}
    a=Analysis_tel(result)
    a.analysistel()

