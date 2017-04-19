# coding=utf-8
import random
import base64
import logging
from scrapy.downloadermiddlewares.retry import RetryMiddleware

# 代理服务器（动态代理）
proxyServer = "http://proxy.abuyun.com:9020"

# 代理隧道验证信息（需要购买）
proxyUser = ""  
proxyPass = ""  

proxyAuth = "Basic " + base64.b64encode(proxyUser + ":" + proxyPass)


class RandomUserAgent(object):
    """Randomly rotate user agents based on a list of predefined ones"""

    def __init__(self, agents):
        self.agents = agents

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getlist('USER_AGENTS'))

    def process_request(self, request, spider):
        request.headers.setdefault('User-Agent', random.choice(self.agents))


class ProxyMiddleware(object):

    def process_request(self, request, spider):

        if not request.headers.get("flag"):
            request.meta["proxy"] = proxyServer
            request.headers["Proxy-Authorization"] = proxyAuth
        return None
        # 可以使用固定代理池，不适用此处
        # proxy = random.choice(PROXIES)
        # # if proxy['user_pass'] is not None:
        # request.meta['proxy'] = "http://%s" % proxy['ip_port']
        # encoded_user_pass = base64.encodestring(proxy['user_pass'])
        # request.headers[
        #     'Proxy-Authorization'] = 'Basic ' + encoded_user_pass
        # print "**************ProxyMiddleware have pass************" + proxy['ip_port']
        # else:
        #     print "**************ProxyMiddleware no pass************" + proxy['ip_port']
        #     request.meta['proxy'] = "http://%s" % proxy['ip_port']



