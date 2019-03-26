# /usr/bin/env python
# -*- coding: UTF-8 -*-
import hashlib
import time
import random
import string
try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote
import requests
import sys
#reload(sys)
#sys.setdefaultencoding("utf-8")

def get_params(plus_item):
    '''请求时间戳（秒级），用于防止请求重放（保证签名5分钟有效）'''
    t = time.time()
    time_stamp=int(t)

    '''请求随机字符串，用于保证签名不可预测'''
    nonce_str = ''.join(random.sample(string.ascii_letters + string.digits, 10))

    '''应用标志，这里修改成自己的id和key'''
    app_id='2111368055'
    app_key='FE4koFjlE1dwPvMg'

    '''值使用URL编码，URL编码算法用大写字母'''
    text1=plus_item
    text=quote(text1.encode('utf8')).upper()

    '''拼接应用密钥，得到字符串S'''
    sign_before='app_id='+app_id+'&nonce_str='+nonce_str+'&text='+text+'&time_stamp='+str(time_stamp)+'&app_key='+app_key

    '''计算MD5摘要，得到签名字符串'''
    m=hashlib.md5()
    m.update(sign_before.encode('UTF-8'))
    sign=m.hexdigest()
    sign=sign.upper()

    params='app_id='+app_id+'&time_stamp='+str(time_stamp)+'&nonce_str='+nonce_str+'&sign='+sign+'&text='+text

    return params



def get_content(plus_item):
    url = "https://api.ai.qq.com/fcgi-bin/nlp/nlp_textpolar"  # API地址
    params = get_params(plus_item)#获取请求参数
    url=url+'?'+params#请求地址拼接
#     print(url)
    try:
        r = requests.post(url)
        allcontents_json = r.json()
        return allcontents_json["data"]["polar"],allcontents_json["data"]["confd"],allcontents_json["data"]["text"]
    except Exception as e:
        print ('a', str(e))
        return 0,0,'0'

if __name__ == '__main__':
    polar,confd,text=get_content('刚刚在肥城仪阳崇文路上，外卖小哥耳机线把喉割开了，意外无处不在啊，骑电车带耳机真的很危险[尴尬][尴尬][尴尬]')
    print('情感倾向：'+ str(polar)+ '\n'+'程度：'+ str(confd)+'\n'+'文本：' + text)