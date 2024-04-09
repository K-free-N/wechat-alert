# -*- coding: UTF-8 -*-
from doctest import debug_script
from pydoc import describe
from flask import jsonify
import requests
import json
import datetime
import sys

def parse_time(*args):
    times = []
    for dates in args:
        eta_temp = dates
        if len(eta_temp.split('.')) >= 2:
            if 'Z' in eta_temp.split('.')[1]:
                s_eta = eta_temp.split('.')[0] + '.' + eta_temp.split('.')[1][-5:]
                fd = datetime.datetime.strptime(s_eta, "%Y-%m-%dT%H:%M:%S.%fZ")
            else:
                eta_str = eta_temp.split('.')[1] = 'Z'
                fd = datetime.datetime.strptime(eta_temp.split('.')[0] + eta_str, "%Y-%m-%dT%H:%M:%SZ")
        else:
            fd = datetime.datetime.strptime(eta_temp, "%Y-%m-%dT%H:%M:%SZ")
        eta = (fd + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S.%f")
        times.append(eta)
    return times

def alert(status,alertnames,levels,times,pod_name,ins,instance,description,count=None):
    if count == 2:
        return "## <font color=\"red\">告警通知: {0}</font>\n**告警名称:** <font color=\"warning\">{1}</font>\n**告警级别:** {2}\n**告警时间:** {3}\n**Pod名称**: {4}\n{5}: {6}\n**告警详情:** <font color=\"comment\">{7}</font>\n".format(status,alertnames,levels,times[0],pod_name,ins,instance,description)
    else:
        params = json.dumps({
            "msgtype": "markdown",
            "markdown":
                {
                    "content": "## <font color=\"red\">告警通知: {0}</font>\n**告警名称:** <font color=\"warning\">{1}</font>\n**告警级别:** {2}\n**告警时间:** {3}\n**Pod名称**: {4}\n{5}: {6}\n**告警详情:** <font color=\"comment\">{7}</font>".format(status,alertnames,levels,times[0],pod_name,ins,instance,description)
                }
            })

    return params

def recive(status,alertnames,levels,times,pod_name,ins,instance,description,count=None):
    if count == 2:
        return "## <font color=\"info\">恢复通知: {0}</font>\n**告警名称:** <font color=\"warning\">{1}</font>\n**告警级别:** {2}\n**告警时间:** {3}\n**恢复时间:** {4}\n**Pod名称:** {5}\n{6}: {7}\n**告警详情:** <font color=\"comment\">{8}</font>\n".format(status,alertnames,levels,times[0],times[1],pod_name,ins,instance,description)
    else:
        params = json.dumps({
            "msgtype": "markdown",
            "markdown":
                {
                    "content": "## <font color=\"info\">恢复通知: {0}</font>\n**告警名称:** <font color=\"warning\">{1}</font>\n**告警级别:** {2}\n**告警时间:** {3}\n**恢复时间:** {4}\n**Pod名称:** {5}\n{6}: {7}\n**告警详情:** <font color=\"comment\">{8}</font>".format(status,alertnames,levels,times[0],times[1],pod_name,ins,instance,description)
                }
            })

    return params

def webhook_url(params,url_key):
    headers = {"Content-type": "application/json"}
    """
    *****重要*****
    """
    url = "{}".format(url_key)
    r = requests.post(url,params,headers)

def send_alert(json_re,url_key):
    print(json_re)
    params = {
        "msgtype": "markdown",
        "markdown":
            {
                "content": ""
            }
        }
    
    if len(json_re['alerts']) != 1:
        for i in json_re['alerts']:
            if i['status'] == 'firing':
                if "instance" in i['labels'] and "pod" in i['labels']:
                    if "description" in i['annotations']:
                        params['markdown']['content'] += alert(i['status'],i['labels']['alertname'],i['labels']['severity'],parse_time(i['startsAt']),i['labels']['pod'],'故障实例',i['labels']['instance'],i['annotations']['description'],2)
                    elif "message" in i['annotations']:
                        params['markdown']['content'] += alert(i['status'],i['labels']['alertname'],i['labels']['severity'],parse_time(i['startsAt']),i['labels']['pod'],'故障实例',i['labels']['instance'],i['annotations']['message'],2)
                    else:
                        params['markdown']['content'] += alert(i['status'],i['labels']['alertname'],i['labels']['severity'],parse_time(i['startsAt']),i['labels']['pod'],'故障实例',i['labels']['instance'],'Service is wrong',2)
                elif "namespace" in i['labels']:
                    params['markdown']['content'] += alert(i['status'],i['labels']['alertname'],i['labels']['severity'],parse_time(i['startsAt']),'None','名称空间',i['labels']['namespace'],i['annotations']['description'],2)

            elif i['status'] == 'resolved':
                if "instance" in i['labels']:
                    if "description" in i['annotations']:
                        params['markdown']['content'] += recive(i['status'],i['labels']['alertname'],i['labels']['severity'],parse_time(i['startsAt'],i['endsAt']),i['labels']['pod'],'故障实例',i['labels']['instance'],i['annotations']['description'],2)
                    elif "message" in i['annotations']:
                        params['markdown']['content'] += recive(i['status'],i['labels']['alertname'],i['labels']['severity'],parse_time(i['startsAt'],i['endsAt']),i['labels']['pod'],'故障实例',i['labels']['instance'],i['annotations']['message'],2)
                    else:
                        params['markdown']['content'] += recive(i['status'],i['labels']['alertname'],i['labels']['severity'],parse_time(i['startsAt'],i['endsAt']),i['labels']['pod'],'故障实例',i['labels']['instance'],'Service is wrong',2)
                elif "namespace" in i['labels']:
                    params['markdown']['content'] += recive(i['status'],i['labels']['alertname'],i['labels']['severity'],parse_time(i['startsAt'],i['endsAt']),'None','名称空间',i['labels']['namespace'],i['annotations']['description'],2)
                elif "Watchdog" in i['labels']['alertname']:
                    webhook_url(alert(i['status'],i['labels']['alertname'],'0','0','0','故障实例','自测','0'),url_key)
        print(params,'<====================>')
        webhook_url(json.dumps(params),url_key)
            
    else:
        for i in json_re['alerts']:
            if i['status'] == 'firing':
                if "instance" in i['labels'] and "pod" in i['labels']:
                    if "description" in i['annotations']:
                        webhook_url(alert(i['status'],i['labels']['alertname'],i['labels']['severity'],parse_time(i['startsAt']),i['labels']['pod'],'故障实例',i['labels']['instance'],i['annotations']['description']),url_key)
                    elif "message" in i['annotations']:
                        webhook_url(alert(i['status'],i['labels']['alertname'],i['labels']['severity'],parse_time(i['startsAt']),i['labels']['pod'],'故障实例',i['labels']['instance'],i['annotations']['message']),url_key)
                    else:
                        webhook_url(alert(i['status'],i['labels']['alertname'],i['labels']['severity'],parse_time(i['startsAt']),i['labels']['pod'],'故障实例',i['labels']['instance'],'Service is wrong'),url_key)
                elif "namespace" in i['labels']:
                    webhook_url(alert(i['status'],i['labels']['alertname'],i['labels']['severity'],parse_time(i['startsAt']),'None','名称空间',i['labels']['namespace'],i['annotations']['description']),url_key)
                elif "Watchdog" in i['labels']['alertname']:
                    webhook_url(alert(i['status'],i['labels']['alertname'],'0','0','0','故障实例','自测','0'),url_key)
            elif i['status'] == 'resolved':
                if "instance" in i['labels']:
                    if "description" in i['annotations']:
                        webhook_url(recive(i['status'],i['labels']['alertname'],i['labels']['severity'],parse_time(i['startsAt'],i['endsAt']),i['labels']['pod'],'故障实例',i['labels']['instance'],i['annotations']['description']),url_key)
                    elif "message" in i['annotations']:
                        webhook_url(recive(i['status'],i['labels']['alertname'],i['labels']['severity'],parse_time(i['startsAt'],i['endsAt']),i['labels']['pod'],'故障实例',i['labels']['instance'],i['annotations']['message']),url_key)
                    else:
                        webhook_url(recive(i['status'],i['labels']['alertname'],i['labels']['severity'],parse_time(i['startsAt'],i['endsAt']),i['labels']['pod'],'故障实例',i['labels']['instance'],'Service is wrong'),url_key)
                elif "namespace" in i['labels']:
                    webhook_url(recive(i['status'],i['labels']['alertname'],i['labels']['severity'],parse_time(i['startsAt'],i['endsAt']),'None','名称空间',i['labels']['namespace'],i['annotations']['description']),url_key)
                elif "Watchdog" in i['labels']['alertname']:
                    webhook_url(alert(i['status'],i['labels']['alertname'],'0','0','0','故障实例','自测','0'),url_key)
