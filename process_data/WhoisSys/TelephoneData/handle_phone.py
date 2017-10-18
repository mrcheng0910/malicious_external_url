#!/usr/bin/env python
# encoding:utf-8

import MySQLdb
import socket
import sys
from analysis_phone import Analysis_tel

reload(sys)
sys.setdefaultencoding('utf8')


class Handle_tel(object):
    def __init__(self):
        self.conn2 = MySQLdb.connect(host="172.29.152.249", user="root", passwd="platform", db="location",charset='utf8')
        self.cursor2 = self.conn2.cursor()
        # 取出要匹配的国内区号，全部的数据源信息均在此库中
        sql2 = "SELECT * FROM telphone"
        self.cursor2.execute(sql2)
        self.results = self.cursor2.fetchall()  # 固话的区号数据源
        self.conn2.commit()


    #设置十进制数的某一位为另一个数
    def wei(self,flag, digit, direct):
        #flag:source; digit:change which; direct:change digit to what
        front = 10 ** digit
        back = 10 ** (digit - 1)
        return int(flag/front)*front + direct*back + flag%back

    def is_x(self,phone,s):#判断待解析电话中是否含有某个字符,如：+86.01051667567 x861
        return phone.find(s)  ##返回-1,查找不到返回-1


    def is_86(self,phone_right):
        if(phone_right[0:2]=="86" or phone_right[0:3]=="086" or phone_right[0:4]=="0086"):#小数点后重复了86或086
            return 1
        else:
            return 0

    #首先处理较异常的电话，在电话中没有带x且没有86重复的情况下，中国地区的
    def handle_special(self,phone_right):
        global flag_all
        global ty_n
        global nu_n
        # phone_right = phone.split('.')[1]
        if (len(phone_right) >= 5):  # 位数在正确的范围内
            n = len(phone_right)
            i1 = phone_right[0]  # 每位都重复
            i2 = phone_right[0:2]  # 两位一重复
            i3=phone_right[0:3]#三位一重复
            if ((phone_right.count(i1) == n or phone_right.count(i2) == n/2) or (phone_right.count(i3)==n/3 and len(phone_right)>=6)):  # 有一定重复规律的电话号码可能是假的，置为5
                ty_n = "5"
                nu_n=phone_right
                flag_all=1
            elif (len(phone_right) == 5 or len(phone_right) == 6):  # 5位或者6位，没有重复错的，可能是服务电话，置为7
                ty_n = "7"
                nu_n=phone_right
                flag_all=1
        else:# 位数小于5位的，位数错误电话，置为6
            ty_n = "6"
            nu_n=phone_right
            flag_all=1

    #处理正常电话，在排除不正常的情况下，根据所判断出的类型进行处理
    def phone_normal(self,phone_right,flag):
        global flag_all
        global posi_n
        global nu_n
        global ty_n
        if(flag==11):#首位不为0的位数为10的可能是11位标准固话少了0,置11
            str = "0"
            phone_new = str + phone_right  # 补成标准11位固话格式
            for row in self.results:
                quhao = row[1]
                length = len(quhao)
                phone_quhao = phone_new[0:length]  # 补0之后的区号位
                nu_n = phone_new[length:]
                if (quhao == phone_quhao):  # 存在该区号，说明为固定电话
                    posi_n = phone_quhao[1:]  # 原来的区号位段
                    ty_n="11"
                    flag_all=1
            if(flag_all==0):
                if(phone_right[0:3]=="400" or phone_right[0:3]=="800"):#首位不为0，位数为10的解析不了成固话，那若是400打头，则可能是服务电话
                    ty_n="4"
                    nu_n=phone_right
                    flag_all=1
                elif(phone_right[0]=="1" and phone_right[1]!="0"):#首位为1,第二位非0，可能是位数不对的手机号，置为03
                    ty_n="03"
                    nu_n=phone_right
                    flag_all=1
                else :#首位不为0的10位数，不是固话，不是400也不是手机号少位，可能是10位数的服务电话，置为2
                    ty_n="2"
                    nu_n=phone_right
                    flag_all=1
        elif(flag==12):#标准的12位固话，即首位是0的
            for row2 in self.results:
                quhao = row2[1]
                length = len(quhao)
                phone_quhao = phone_right[0:length]
                nu_n = phone_right[length:]
                if (quhao == phone_quhao):  # 存在该区号，说明为固定电话
                    ty_n = "12"
                    posi_n=phone_quhao
                    flag_all=1
            if (flag_all == 0):  # 前面有0的12位的，找不到对应的固话，可能是手机号前面多了个0，置02
                ty_n = "02"
                posi_n="0"
                flag_all=1
                nu_n= phone_right[1:]
        elif(flag==13):#12位固话前面少了0，即总共11位且首位不为0的情况，置13
            str = "0"
            phone_new = str + phone_right  # 补成标准12位固话格式
            for row2 in self.results:
                quhao = row2[1]
                length = len(quhao)
                phone_quhao = phone_new[0:length]  # 补0之后的区号位
                phone_quhao_init = phone_quhao[1:]  # 原来的区号位段
                phone_number = phone_new[length:]
                if (quhao == phone_quhao):  # 存在该区号，说明为固定电话
                    ty_n = "13"
                    posi_n=phone_quhao_init
                    nu_n=phone_number
                    flag_all=1
            if (flag_all == 0):  # 11位但不是12位的固话少了0，则若首位是1第二位非0，应该是标准手机号段，置0
                if(phone_right[0]=="1" and phone_right[1]!=0):
                    flag_all=1
                    ty_n="0"
                    nu_n=phone_right
                else:#11位非0打头，不是固话少0，也不是手机号，置为存疑电话或者是11位数的服务电话，置8
                    ty_n="8"
                    flag_all=1
                    nu_n=phone_right
        elif(flag==1):#标准的11位固定电话或者是非11位、12位的电话，即首位是0的，置为1
            for row2 in self.results:
                quhao = row2[1]
                length = len(quhao)
                phone_quhao = phone_right[0:length]
                phone_number = phone_right[length:]
                if (quhao == phone_quhao):  # 存在该区号，说明为固定电话
                    if(len(phone_right)==11):
                        ty_n= "1" #标准固话解析得了
                    else:
                        ty_n="14" #位数不对但解析得了
                    flag_all=1
                    posi_n=phone_quhao
                    nu_n=phone_number
            if(flag_all==0):
                if(len(phone_right)==11):#首位是0可能是固话，解析不了置为10
                    ty_n="10"
                    nu_n=phone_right
                    flag_all=1
                else:#首位是0的非11位或者是12位，解析不了的，置为140
                    ty_n="140"
                    nu_n=phone_right
                    flag_all=1

    def handle(self,phone):#电话号段中没有x的且没有86重复的
        global flag_all
        global country_n
        global country
        global posi_n
        global nu_n
        global ty_n
        phone_right = phone.split('.')[1]
        Handle_tel.handle_special(self,phone_right)#先处理异常
        if(flag_all==0):#不在异常电话范围内
            if (phone_right[0]=="0"):  # 国内标准固定电话或非标准手机号格式
                if (len(phone_right)!=12):  # 若为11位，则可能是标准固话，置为1，否则首位是0的小于11位或者大于12位的，可能是位数不对的固话格式
                    Handle_tel.phone_normal(self,phone_right,1)
                elif (len(phone_right) == 12):  # 固定电话的12位标准格式，置12，含非标准手机号，即前面多了0
                    Handle_tel.phone_normal(self,phone_right, 12)

            elif (phone_right[0]!="0"):
                # 小数点后非0，10位数则可能是标准固话少了0，11位可能是12位固话少了0,或者是手机号
                if (len(phone_right) == 11):  # 首位不是0的11位的可能是12位固话少了0，即区号“01或1以上”打头的，置13，含手机号的
                    Handle_tel.phone_normal(self,phone_right, 13)

                elif (len(phone_right) == 10):  # 首位非0位数为10位的，可能是标准固话少了0，即“01或以上”打头的，置11
                    Handle_tel.phone_normal(self,phone_right, 11)

                else:
                    if(phone_right[0]=="1" and phone_right[1] !="0"):#首位是1，第二位非0的，可能是是位数不对的手机号，置为03
                        ty_n="03"
                        nu_n=phone_right
                        flag_all=1
                    elif(len(phone_right)==7 or len(phone_right)==8 or len(phone_right)==9):#首位非0的7,8,9位，排除是手机号的可能，则可能是固话少了区号位，置15
                        ty_n="15"
                        nu_n=phone_right
                        flag_all=1
                    else:#只剩下位数大于11的，置为存疑电话或服务电话，置9
                        ty_n="9"
                        nu_n=phone_right
                        flag_all=1

    def handle_phone(self,phone_num):

        result = {
            "country_n": "",
            "posi_n": "",
            "nu_n": "",
            "country": "",
            "ty_n" : "",
            "flag" : "",
            "province" : "",
            "city" : ""
        }
        try:
            global count
            count=0
            phone = phone_num
            if phone is not None:
                global flag_all
                global country
                global country_n
                global posi_n
                global nu_n
                global ty_n
                flag_all = 0
                country=""
                country_n=""
                posi_n=""
                nu_n=""
                ty_n=""
                if (Handle_tel.is_x(self,phone,".") != -1):#有小数点，但小数点的位置不一定对
                    if(phone=="+."):
                        ty_n="31"
                        nu_n=phone
                        flag_all=1
                    else:
                        phone_left = phone.split('.')[0]
                        phone_right = phone.split('.')[1]
                        if (phone_left == "+86" or phone_left == "+086"):
                            country_n=phone_left
                            country="中国"
                            if(phone_right==""):
                                ty_n="6"
                                flag_all=1
                            else:
                                if(phone_right[0]!="+"):#小数点后面没有加号则正常处理
                                    if (Handle_tel.is_x(self,phone,"x") == -1 and Handle_tel.is_86(self,phone_right) == 0):
                                        Handle_tel.handle(self,phone)
                                    elif (Handle_tel.is_x(self,phone,"x") == -1 and Handle_tel.is_86(self,phone_right) == 1):  # 无带x的，但有86重复的
                                        if (phone_right[0:2] == "86"):
                                            phone_new = "+86." + phone_right[2:]
                                            Handle_tel.handle(self,phone_new)
                                        elif (phone_right[0:3] == "086"):
                                            phone_new = "+086." + phone_right[3:]
                                            Handle_tel.handle(self,phone_new)
                                        elif (phone_right[0:4] == "0086"):
                                            phone_new = "0086." + phone_right[4:]
                                            Handle_tel.handle(self,phone_new)
                                    elif (Handle_tel.is_x(self,phone,"x") != -1):  # 有带x的
                                        phone_last = phone[Handle_tel.is_x(self,phone,"x"):]  # “x123”
                                        phone_new = phone[0:Handle_tel.is_x(self,phone,"x")].strip()  # 去掉后面的带“x”的部分剩下的电话号段
                                        Handle_tel.handle(self,phone_new)
                                        if (flag_all == 1):  # 该号段可以被处理
                                            nu_n=nu_n+phone_last
                                else:#小数点后面有加号的
                                    if(phone_right[0:3]=="+86"):
                                        phone_new="+86."+phone_right[3:]
                                        Handle_tel.handle(self,phone_new)
                                    elif(phone_right[0:4]=="+086"):
                                        phone_new="+086."+phone_right[4:]
                                        Handle_tel.handle(self,phone_new)
                                    else:
                                        ty_n="30"
                                        nu_n=phone_right
                                        flag_all=1
                        else:
                            country_n=phone_left
                            country="外国"
                            ty_n="3"
                            flag_all=1
                else:  # 电话中没有小数点，可能是都没有标号，也可能是靠着“-”分开的,还有可能是靠着括号分开的
                    if(phone=="CN" or phone=="NA"):
                        ty_n="31"
                        nu_n=phone
                        flag_all=1
                    else:
                        if(Handle_tel.is_x(self,phone,"-")==-1 and Handle_tel.is_x(self,phone,"(")==-1):#电话中没有“-”分开号段的，，也没有“（”分开的
                            if (phone[0:3] == "+86"):
                                phone_new=phone[0:3]+"."+ phone[3:]
                                country_n="+86"
                                country="中国"
                                Handle_tel.handle(self,phone_new)
                            elif(phone[0:4]=="+086"):
                                phone_new =phone[0:4]+"."+phone[4:]
                                country_n = "+086"
                                country="中国"
                                Handle_tel.handle(self,phone_new)
                            else:
                                ty_n="30"
                                nu_n=phone
                                flag_all=1
                        elif(Handle_tel.is_x(self,phone,"-")!=-1 and Handle_tel.is_x(self,phone,"(")==-1):#电话是靠着“-”分开的,但不含“（”
                            if(phone[0:3]=="+86" or phone[0:4]=="+086"):
                                country_n = "+86"
                                country="中国"
                                if(phone.count('-')==1):
                                    phone_new = "+86." + phone.split('-')[1]
                                    print phone_new
                                    Handle_tel.handle(self,phone_new)
                                elif(phone.count('-')==2):
                                    phone_new = "+86." + phone.split('-')[1] + phone.split('-')[2]
                                    Handle_tel.handle(self,phone_new)

                            else:
                                country_n = "+86"
                                country = "中国"
                                if(phone.count('-')==1):
                                    phone_new = "+86." + phone.split('-')[0] + phone.split('-')[1]
                                    Handle_tel.handle(self,phone_new)
                        elif(Handle_tel.is_x(self,phone,"(")!=-1 and Handle_tel.is_x(self,phone,"-")==-1):#电话靠着"("分开的,且没有“-”
                            f1=Handle_tel.is_x(self,phone,"(")
                            phone1=phone[f1+1:]
                            phone_left=phone1.split(')')[0]
                            phone_right=phone1.split(')')[1]
                            if(phone_left=="86"):
                                phone_new="+86."+phone_right
                            else:
                                phone_new="+86."+phone_left+phone_right
                            country_n="+86"
                            country="中国"
                            Handle_tel.handle(self,phone_new)
                        else:
                            phone1= phone.replace("(","")
                            phone2=phone1.replace(")","")
                            phone3=phone2.replace("-","")
                            phone3=phone3.replace(" ","")
                            if(phone3[0:2]=="86"):
                                phone_new="+86."+phone3[2:]
                                country="中国"
                                country_n="+86"
                                Handle_tel.handle(self,phone_new)
                            else:
                                ty_n="30"
                                nu_n=phone
                                country="外国"
                if(flag_all==1):
                    result = {
                        "country_n": country_n,
                        "posi_n": posi_n,
                        "nu_n": nu_n,
                        "country": country,
                        "ty_n": ty_n,
                        "province": "",
                        "city": ""
                    }
                    result = Analysis_tel(result).analysistel().result
            else:
                pass
        except:
            pass
        return result

    def handletel(self,phone_num):
        self.conn2.close()
        return Handle_tel.handle_phone(self,phone_num)




if __name__ == "__main__":
    h=Handle_tel()
    a=h.handletel('+86.1065985888')
    print a




