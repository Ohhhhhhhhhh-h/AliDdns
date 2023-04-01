# --coding:utf-8--
#   @Author:    Alpaca
#   @Time:      2022/12/3 19:26
#   @Software:  PyCharm
#   @File:      main

import json
import os
import re
import sys

from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkcore.client import AcsClient

ak_id = ''
ak_s = ''
ipv6 = ''
domain_name_list = []
length = 0
param_remind = """请在params.json中添加配置\n示例：\n
            {
              "access-key-id": "你的access-key-id",
              "access-key-secret": "你的access-key-secret",
              "domain_name_list": [
                "你的域名",
                "你的第二个域名"
              ]
            }"""


def get_dns_record(domain_name):  # 获取dns记录
    credentials = AccessKeyCredential(ak_id, ak_s)

    client = AcsClient(region_id='cn-hangzhou', credential=credentials)
    request = DescribeDomainRecordsRequest()
    request.set_accept_format('json')
    request.set_DomainName(domain_name)
    request.set_Type("AAAA")
    try:
        response = client.do_action_with_exception(request)
    except:
        print(f'参数错误{param_remind}')
        input('按下enter以退出')
        sys.exit()
    return json.loads(response)


def update_dns_record(rr, record_id):  # 更新dns记录
    global length
    credentials = AccessKeyCredential(ak_id, ak_s)

    client = AcsClient(region_id='cn-hangzhou', credential=credentials)
    request = UpdateDomainRecordRequest()
    request.set_accept_format('json')
    request.set_TTL(600)
    request.set_Value(ipv6)
    request.set_Type("AAAA")
    request.set_RR(rr)
    request.set_RecordId(record_id)
    try:
        response = client.do_action_with_exception(request)
        length += 1
    except ServerException as se:
        response = se
        print(str(response))
    return str(response)


def start():
    global domain_name_list, ak_s, ak_id, ipv6
    if not os.path.exists('params.json'):
        statu = True
        print('初次使用请配置以下参数\n')
        while statu:
            if not ak_id:
                ak_id = input('请输入access-key-id:\n')
            if not ak_s:
                ak_s = input('请输入access-key-secret:\n')
            if not domain_name_list:
                domain_name_list = input('请输入需要更新ipv6地址的域名，如有多个域名请使用半角逗号“，”分隔\n')
                if domain_name_list:
                    domain_name_list = domain_name_list.split(',')
            if ak_s and ak_id and domain_name_list:
                statu = False
            else:
                print('请重新输入\n')
        for index in range(len(domain_name_list)):
            domain_name_list[index] = domain_name_list[index].strip()
        d2j = json.dumps({
            'access-key-id': ak_id,
            'access-key-secret': ak_s,
            "domain_name_list": domain_name_list
        })
        with open("params.json", mode="w", encoding="utf-8") as fp:
            fp.write(d2j)
    else:
        with open("params.json", mode="r", encoding="utf-8") as fp:
            params = json.load(fp)
        if not params:
            print(param_remind)
        try:
            ak_id = params["access-key-id"]
            ak_s = params["access-key-secret"]
            domain_name_list = params["domain_name_list"]
        except KeyError:
            print(param_remind)
    text = os.popen('ipconfig /all').read()
    if re.findall(r"IPv6 地址 . . . . . . . . . . . . : (.*?)\(", text, re.I):
        ipv6 = re.findall(r"IPv6 地址 . . . . . . . . . . . . : (.*?)\(", text, re.I)[0]
        print('ipv6:' + ipv6)
    else:
        print('无ipv6地址')
        sys.exit()


    resp = ''
    for domain_name in domain_name_list:
        resp = get_dns_record(domain_name)
        record_list = resp['DomainRecords']['Record']
        for record in record_list:
            if record["Value"] == ipv6:
                continue
            resp = resp + update_dns_record(record['RR'], record['RecordId'])
    return f"{resp}\n更新了{length}条记录"


if __name__ == '__main__':
    start()
