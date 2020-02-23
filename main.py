#!/usr/bin/env python
# coding=utf-8
from flask import Flask
from flask import request
from flask import make_response
from flask import jsonify
import sys
import requests
import json

reload(sys)
sys.setdefaultencoding('utf8')

try:
    from urllib.parse import urlparse
except:
    from urlparse import urlparse

app = Flask(__name__)

base_path = ''
dedata = {'ret': 0, 'msg': "success"}

# 企业微信群机器人的webhook地址
bot_url = ""

def send2Bot(md):
    url = bot_url
    headers = {'Content-Type': 'application/json'}
    requestData = {"msgtype": "markdown", "markdown": {"content": md}}

    r = requests.post(url, data=json.dumps(requestData))

@app.route('/', methods=['POST'])
def home():
    dict_data = {"sss": "ddd"}
    eventType = "ddd"
    # 接受json数据
    a = request.get_data(as_text=True)
    print("the a is ------- " + a)
    # 防止接口改变后，无法识别其他类型的数据并crash
    if a and a != "":
        try:
            dict_data = json.loads(a)
        except:
            dict_data = {"sss": "ddd"}

    if dict_data.has_key("eventType"):
        eventType = dict_data["eventType"]

    md = ("<font color=\"warning\">警告：</font> "
          +"收到了无法解析的数据，请检查bugly接口文档是否更新。 \n" 
          + str(a))

    if eventType == "bugly_crash_trend":
        eventContent = dict_data["eventContent"]
        appName = eventContent["appName"]
        mDate = eventContent["date"]
        mDatas = eventContent["datas"]
        data_MD_content = ""
        all_acess_user = 0
        all_crash_user = 0

        for i in mDatas:
            print(i)
            # 崩溃率保留2位小数
            prop = "%.2f%%" % (
                float(i["crashUser"]) / float(i["accessUser"]) * 100)
            data_MD_content += ("> " + str(i["version"]) + "版本: "
                                + "联网用户<font color=\"info\">" +
                                str(i["accessUser"]) + "</font>人, "
                                + "崩溃率<font color=\"warning\">" + str(prop) + "</font> \n")

            all_acess_user += int(i["accessUser"])
            all_crash_user += int(i["crashUser"])

        md = ""
        md += ("**" + appName + "**" + " 每日统计 - " + mDate + " \n"
               + "总联网人数: <font color=\"info\">" +
               str(all_acess_user) + "</font>, "
               + "总崩溃人数: <font color=\"warning\">" +
               str(all_crash_user) + "</font> \n"
               + data_MD_content)

    elif eventType == "bugly_tag":
        eventContent = dict_data["eventContent"]
        appName = eventContent["appName"]
        mDate = eventContent["date"]
        mDatas = eventContent["datas"]
        data_MD_content = ""

        for i in mDatas:
            print(i)
            data_MD_content += ("> " + str(i["tagName"]) + ": "
                                + "崩溃用户<font color=\"warning\">" +
                                str(i["crashUser"]) + "</font>, "
                                + "崩溃次数<font color=\"warning\">" + str(i["crashCount"]) + "</font> \n")

        md = ""
        md += ("**" + appName + "**" + " Tag统计 - " + mDate + " \n"
               + data_MD_content)

    send2Bot(md)
    return (jsonify(dedata))


def handler(environ, start_response):
    parsed_tuple = urlparse(environ['fc.request_uri'])
    li = parsed_tuple.path.split('/')
    global base_path
    if not base_path:
        base_path = "/".join(li[0:5])
    return app(environ, start_response)
