# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LianhangItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    scan_time = scrapy.Field()
    departure_dates = scrapy.Field()
    departure_date = scrapy.Field()
    departure_route = scrapy.Field()
    arrival_route = scrapy.Field()
    flight = scrapy.Field()
    departure_time = scrapy.Field()
    arrival_time = scrapy.Field()
    red = scrapy.Field()
    ticket_price = scrapy.Field()
    surplus = scrapy.Field()
    pm_type = scrapy.Field()
    before_takeoff_2 = scrapy.Field()
    take_off_2 = scrapy.Field()
    times = scrapy.Field()
    airway = scrapy.Field()
    off_site = scrapy.Field()
