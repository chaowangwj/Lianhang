# from scrapy.contrib.throttle import AutoThrottle
from scrapy.extensions.throttle import AutoThrottle
import logging
import re
# should use a adapter to wrap AutoThrottle, but I am lazy....

class AutoThrottleWithList(AutoThrottle):
    ''' AutoThrottle with a name list so that the spider limits its 
        speed only for the sites on the list '''

    # param: site_list: list contains the domain to be limited 
    def __init__(self, crawler):
        self.limit_list = crawler.settings.getdict("LIMIT_SITES")
        super(AutoThrottleWithList, self).__init__(crawler)

    def _adjust_delay(self, slot, latency, response):
        """override AutoThrottle._adjust_delay()"""
        reg = re.search(r'http[s]?://([^/]+).*', response.url)
        res_domain = reg.group(1)
        slot.delay = 0.1
        if res_domain in self.limit_list:
            slot.delay = 0.2
        
        