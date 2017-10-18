# encoding:utf-8

"""
使用内部DNS服务器获取域名的CNAME记录
作者：程亚楠
时间：2017.8.25
"""

import DNS


domains = (
u'fuchubao.com.cn', u'cuntie.com.cn', u'cunhun.com.cn', u'kedipu.com.cn', u'qiliaofa.com.cn', u'qinggeer.com.cn',
u'chunka.com.cn', u'xianzuke.com.cn', u'yakesi.com.cn', u'citsa.com.cn', u'aidengpu.com.cn', u'srp360.com.cn',
u'faremo.com.cn', u'hongnice.com.cn', u'yilaige.com.cn', u'wjpump.com.cn', u'heiergo.com.cn', u'congshen.com.cn',
u'yikaopai.com.cn', u'oheman.com.cn', u'kelama.com.cn', u'dianjuan.com.cn', u'wandouya.com.cn', u'gzgaoke.com.cn',
u'cgszg.com.cn', u'daituo.com.cn', u'chaome.com.cn', u'zyqczj.com.cn', u'lidaxiao.com.cn', u'lawufu.com.cn',
u'mimixiu.com.cn', u'zhimayan.com.cn', u'choude.com.cn', u'xinyilun.com.cn', u'chaodeyi.com.cn', u'starmei.com.cn',
u'bingla.com.cn', u'ebling.com.cn', u'xueyabao.com.cn', u'choudong.com.cn', u'jzdzs.com.cn', u'haodela.com.cn',
u'ca110.com.cn', u'pkofx.com.cn', u'jinpinzi.com.cn', u'weigezi.com.cn', u'xxhd99.com.cn', u'ygcxwc.com.cn',
u'choukuai.com.cn', u'chouqi.com.cn', u'getidai.com.cn', u'xjaziz.com.cn', u'changshe.com.cn', u'haowaner.com.cn',
u'aiziwei.com.cn', u'szdsxmp.com.cn', u'duanding.com.cn', u'boyikao.com.cn', u'shiruida.com.cn', u'chunzuan.com.cn',
u'dgyougu.com.cn', u'jialide.com.cn', u'taojinle.com.cn', u'lemadao.com.cn', u'yaoyedai.com.cn', u'hldqf.com.cn',
u'nicchu.com.cn', u'haimitao.com.cn', u'laiwabao.com.cn', u'mimaimai.com.cn', u'ylfs168.com.cn', u'lepaisi.com.cn',
u'hao923.com.cn', u'penzaige.com.cn', u'dizuan.com.cn', u'zhiweibo.com.cn', u'maikaiwo.com.cn', u'yuyandi.com.cn',
u'zhixueke.com.cn', u'makebang.com.cn', u'abuai.com', u'178fg.com', u'93crm.com', u'91aoe.com', u'abo4.com',
u'irjk8.com', u'402460.com.cn', u'onvba.com', u'bst63.com', u'1zzj.com', u'4won2.com', u'qttxs.com', u'710ld.com',
u'rmst1.com', u'41wp.com', u'19ppt.com', u'ka982.com', u'xqxft.com', u'bt117.com', u'sugata.com.cn', u'yingdang.com.cn',
u'191yzc.com.cn', u'hfkths.com.cn', u'no1ds.com', u'lhoip.com.cn', u'3z999.com', u'coch3.com', u'xieyaban.com.cn',
u'biedong.com.cn', u'877ii.com', u'wzx3.com', u'myytsm.com.cn', u'eoshi.com', u'zd6b.com', u'52gm6.com', u'tamo7.com',
u'snowboy.com.cn', u'acely.com.cn', u'yuefuba.com.cn', u'laolelao.com.cn', u'fudaoshi.com.cn', u'sjdjk.com.cn',
u'heode.com', u'irjif.com', u'vipzk.com.cn', u'ximaide.com.cn', u'dangzhou.com.cn', u'shizihou.com.cn', u'hyhlb.com.cn',
u'oktea.com.cn', u'hxxrm.com', u'24son.com', u'4w8s.com', u'nxeoe.com', u'39dyy.com', u'xd400.com', u'91dzs.com',
u'65lll.com', u'08sow.com', u'686sc.com', u'dwwpl.com', u'anchua.com.cn', u'tqhbjx.com.cn', u'saisung.com.cn',
u'wylco.com.cn', u'52dmy.com', u'17the.com', u'br200.com', u'0d12.com', u'mwqhq.com', u'zs973.com', u'diele.com.cn',
u'anruilai.com.cn', u'wds8558.com.cn', u'shuyiran.com.cn', u'zimutang.com.cn', u'mifulan.com.cn', u'tpcshen.com.cn',
u'ycmcnc.com.cn', u'wj0556.com.cn', u'cunling.com.cn', u'mwqfq.com', u'5k5tv.com', u'hxxnd.com', u'imihu.com.cn',
u'mewenhua.com.cn', u'chabaixi.com.cn', u'afapu.com', u'w88r8.com', u'122zx.com', u'men58.com', u'57fei.com',
u'qgbgp.com', u'qczqk.com', u'710wq.com', u'w88h7.com', u'tp299.com')

domains = [u'220y.com', u'0745a.com', u'120male.com', u'889986.org.cn', u'wuzhoupharm.com', u'baijiajiangtang.com', u'wuhanjinlun.com', u'a265.cn', u'661477.com', u'228044.com', u'china-goldensun.com', u'hidao8.com', u'chica-loca.com', u'v962.cn', u'alawz.com', u'shwgqlz.com', u'13enjoy.com', u'wap2007cp.com', u'cysh158.com', u'7000bet365.com', u'ssz001.com', u'6789ccc.com', u'2000bet365.com', u'pjbet03.com', u'kk3198.cn', u'zfzy8888.com', u'ii3333.com', u'roybet88.com', u'859090.com', u'cdbtr.cn', u'72062.org.cn', u'831599.org.cn', u'828699.org.cn', u'lmc-ele.com', u'sxhecai.com', u'youyidz.com', u'hyzuoxuan.com', u'deemstone.net', u'7wxx.com', u'purefootball.cn', u'44xb.com', u'6hcd.com', u'256789.net', u'ssz003.com', u'778949.com', u'686098.com', u'sixmark88.com', u'ssi00.com', u'easycome8.com', u'jz7700.com', u'dnxia.com', u'jj823.com', u'sihaibo8.com', u'kkk868.com', u'w112.net', u'918fl.com', u'mmcza.com', u'boblg.com', u'5y7y.com', u'6868sz.com', u'md0055.com', u'51bbcn.com', u'zx160.com', u'x88588.com', u'0771mfyz.com', u'zhanghobo.com', u'ya868.com', u'zhoukou99.com', u'rg830.com', u'zhongdaxj.com', u'viagraonlinepharmacywww.com', u'sss336.com', u'996sss.com', u'sss520.com', u'ynccc.com', u'03tz.com', u'se8w.com', u'19iiii.com', u'007gan.com', u'00i9.com', u'xff8.com', u'bjabckj.com', u'chsyzj.com', u'xnjdedu.com', u'ekzbb.com', u'sgouf.com', u'1218889.com', u'6888219.com', u'700737.net', u'talktodo.com', u'11ise.com', u'c2007cp.com', u'924699.com', u'918fl.com', u'6789eee.com', u'slk8888.com', u'78luckcity.com', u'lmc-ele.com']



def domain2cname(domain):
    """
    获取解析到的域名cname列表
    """
    cnames = []
    reqobj = DNS.Request()
    try:
        answerobj_a = reqobj.req(name=domain, qtype=DNS.Type.A, server="222.194.15.253")

        for i in answerobj_a.answers:
            if i['typename'] == 'CNAME':
                cnames.append(i['data'])
    except DNS.Base.DNSError:
        cnames = []

    return cnames



def domain2ip(domain):
    """
    获取解析到的域名cname列表
    """
    ips = []
    reqobj = DNS.Request()
    try:
        # answerobj_a = reqobj.req(name=domain, qtype=DNS.Type.NS, server="222.194.15.253")
        # answerobj_a = reqobj.req(name=domain, qtype=DNS.Type.NS, server="114.114.114.114")
        # answerobj_a = reqobj.req(name=domain, qtype=DNS.Type.NS, server="8.8.8.8")
        answerobj_a = reqobj.req(name=domain, qtype=DNS.Type.A, server="f.gtld-servers.net")


        for i in answerobj_a.answers:
            print i
            # if i['typename'] == 'A':
            #     ips.append(i['data'])
    except DNS.Base.DNSError:
        ips = []

    return ips


domains= ['baidu.com']
# domains = ['www.ifeng.com.lxdns.com']
# domains = ['www.ifeng.com.ifengcdn.com']
for i in domains:
    print domain2ip(i)
#
# print domain2cname('www.chinadaily.com.cn')
# print domain2cname('www.ifeng.com')
