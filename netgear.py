#!/usr/bin/env python

import requests, re, sys, time, datetime, hmac
import paho.mqtt.publish as publish

ip = sys.argv[1]
password = sys.argv[2]
mqtt = sys.argv[3]
topic = sys.argv[4]
delay_stats = int(sys.argv[5])
delay_conf = int(sys.argv[6])
next_stats = next_conf = datetime.datetime.now().timestamp()
lasttime = None
last = dict()

def digest(password):
    count = 0
    space = "\0"
    passwrd = 0

    while count <= (2048 - (len(password) + 1)):
      if count == 0:
        passwrd = password
      else:
        passwrd += password
      passwrd += space
      count += len(password) + 1
    while count < 2048:
      passwrd += space
      count += 1
    return hmac.new("YOU_CAN_NOT_PASS".encode(), passwrd.encode(), 'md5').hexdigest()

while True:
    data = dict()
    if datetime.datetime.now().timestamp() >= next_stats:
        cookie = requests.post('http://{}/login.htm'.format(ip), data={ 'submitId': 'pwdLogin', 'password': digest(password), 'submitEnd': ''})
        r = requests.get('http://{}/config/monitoring_port_statistics.htm'.format(ip), cookies=cookie.cookies)

        for i in r.text.replace("\r", "\n").split('\n'):
            if re.match("StatisticsEntry\[[0-9]+\]", i):
                port = re.sub("StatisticsEntry\[[0-9]+\] = '([^']+)';", r'\1', i).split('?')
                portid = int(port[0])
                if portid not in data.keys():
                    data[portid] = {}
                if lasttime is not None:
                    offset = datetime.datetime.now().timestamp() - lasttime
                    data[portid] = { **data[portid], **{ 'down_spd': int((int(port[1]) - last[portid]['down']) / offset), 'up_spd': int((int(port[2]) - last[portid]['up']) / offset) } }
                data[portid] = { **data[portid], **{ 'down': int(port[1]), 'up': int(port[2]) } }
                last[portid] = data[portid]
                data[portid] = { **data[portid], **{ 'error': port[3]} }
        lasttime = datetime.datetime.now().timestamp()
        next_stats = datetime.datetime.now().timestamp() + delay_stats

    if datetime.datetime.now().timestamp() > next_conf:
        r = requests.get('http://{}/config/status_status.htm'.format(ip), cookies=cookie.cookies)
        for i in r.text.replace("\r", "\n").split('\n'):
            if re.match("portConfigEntry\[[0-9]+\]", i):
                port = re.sub("portConfigEntry\[[0-9]+\] = '([^']+)';", r'\1', i).split('?')
                portid = int(port[0])
                if portid not in data.keys():
                    data[portid] = {}
                data[portid] = { **data[portid], **{ 'name': port[1], 'status': port[2], 'speed': port[3], 'link': port[4]} }
        r = requests.get('http://{}/config/ratelimit_rate_limit.htm'.format(ip), cookies=cookie.cookies)
        for i in r.text.replace("\r", "\n").split('\n'):
            if re.match("portRateEntry\[[0-9]+\]", i):
                port = re.sub("portRateEntry\[[0-9]+\] = '([^']+)';", r'\1', i).split('?')
                portid = int(port[0])
                if portid not in data.keys():
                    data[portid] = {}
                data[portid] = { **data[portid], **{ 'ingress': port[1], 'egress': port[2]} }
        r = requests.get('http://{}/config/broadcastfiltering_broadcast_filtering.htm'.format(ip), cookies=cookie.cookies)
        for i in r.text.replace("\r", "\n").split('\n'):
            if re.match("stormRateEntry\[[0-9]+\]", i):
                port = re.sub("stormRateEntry\[[0-9]+\] = '([^']+)';", r'\1', i).split('?')
                portid = int(port[0])
                if portid not in data.keys():
                    data[portid] = {}
                data[portid] = { **data[portid], **{ 'storm_rate': port[1]} }
        r = requests.get('http://{}/config/portbased_advanced.htm'.format(ip), cookies=cookie.cookies)
        for i in r.text.replace("\r", "\n").split('\n'):
            if re.match("var vlanCfg = ", i):
                port = re.sub("var vlanCfg = '([^']+)';", r'\1', i).split('?')
                portid = 0
                for val in port:
                    portid = portid + 1
                    if portid not in data.keys():
                        data[portid] = {}
                    data[portid] = { **data[portid], **{ 'vlan': val } }
        r = requests.get('http://{}/config/status_switch_info.htm'.format(ip), cookies=cookie.cookies)
        for i in r.text.replace("\r", "\n").split('\n'):
            if re.match("var sysInfo = ", i):
                port = re.sub("var sysInfo = '([^']+)';", r'\1', i).split('?')
                data['sys'] = { 'model': port[0], 'name': port[1], 'mac': port[2], 'version': port[3], 'dhcp': port[4], 'ip': port[5], 'mask': port[6], 'gw': port[7], 'serial': port[8] }
        next_conf = datetime.datetime.now().timestamp() + delay_conf

    msgs = []
    for num, switch in data.items():
        for key, val in switch.items():
            msgs.append({ 'topic': '{}/{}/{}'.format(topic, num, key), 'payload': val })
    if len(msgs):
        publish.multiple(msgs=msgs, hostname=mqtt)
    time.sleep(1)
