#!/usr/bin/env python2
from __future__ import print_function

import os
import sys
import etcd
import json
import time
import base64
import urllib3.exceptions
import requests
from collections import defaultdict

PREFIX = os.environ.get("PROXY_PREFIX", "/proxy")
APIURL = 'http://localhost:8001/api/routes/'

def filter_prefix(d, pref):
    return [k for k in d.keys() if k.startswith("%s/%s/" % (PREFIX, pref))]

class log:
    @staticmethod
    def info(msg):
        print("=> " + msg)
    @staticmethod
    def error(msg, e=None):
        print("=! %s : %s" % (msg, str(e)), file=sys.stderr)

class State:
    def __init__(self):
        self.proxies = set()

class Config:
    def __init__(self, host_ip):
        self.state = State()
        self.client = etcd.Client(host=host_ip, port=4001)

    def sync(self, children):
        etc = dict((child.key, child.value) for child in children)

        proxies = set(k.split('/')[-1] for k in filter_prefix(etc, 'proxies'))
        self.sync_proxies(proxies)

    def create_proxy(self, proxy):
        path = os.path.join(PREFIX, 'proxies', proxy)
        target = self.client.read(path)
        payload = {'target': target.value}
        r = requests.post(APIURL + proxy, data=json.dumps(payload))
        log.info("I added proxy /%s for %s" % (proxy, target.value))

    def delete_proxy(self, proxy):
        # path = os.path.join(PREFIX, 'proxies', proxy)
        r = requests.delete(APIURL + proxy)
        log.info("I deleted proxy /%s" % proxy)

    def sync_proxies(self, proxies):
        proxies_to_add = proxies - self.state.proxies
        for proxy in proxies_to_add:
            log.info("Creating proxy %s" % proxy)
            try:
                self.create_proxy(proxy)
                self.state.proxies.add(proxy)
            except Exception as e:
                log.error("Failed to create proxy %s" % proxy, e)
        proxies_to_rm = self.state.proxies - proxies - {'/'}
        for proxy in proxies_to_rm:
            log.info("Removing proxy %s" % proxy)
            try:
                self.delete_proxy(proxy)
                self.state.proxies.remove(proxy)
            except Exception as e:
                log.error("Failed to remove proxy %s" % proxy, e)

if __name__ == '__main__':
    host_ip = os.environ.get('COREOS_PRIVATE_IPV4', None)
    log.info("Connecting to etcd at %s" % host_ip)

    init = False
    config = Config(host_ip)
    config.client.set(PREFIX + '/service', json.dumps({'host': host_ip, 'port': 8000}))

    while True:
        try:
            if not init:
                r = config.client.read(PREFIX, recursive=True)
                init = True
            else:
                config.client.read(PREFIX, recursive=True, wait=True)
                r = config.client.read(PREFIX, recursive=True)
            config.sync(r.children)
        except urllib3.exceptions.ReadTimeoutError as e:
            time.sleep(1)
        except KeyError as e:
            time.sleep(1)
        except etcd.EtcdException as e:
            time.sleep(1)
