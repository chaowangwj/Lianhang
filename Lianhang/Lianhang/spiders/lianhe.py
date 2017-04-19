# -*- coding: utf-8 -*-
# import scrapy
from scrapy import Spider, FormRequest,Request
import re
import json
from Lianhang.items import LianhangItem
import datetime
import re
from Lianhang.CodeList import CodeList
import hashlib
pubkey = "19EAIRTICKET"


class LianheSpider(Spider):
    url = "http://m.flycua.com/h5/book/flightSearch.html"
    name = "lianhe"
    allowed_domains = ["http://m.flycua.com"]

    # start_urls = (
    #     'http://www.http://m.flycua.com/',
    # )

    def parse(self, response):
        pass

    def start_requests(self):
        """根据需要查询的航班三字码，以及查询日期段（跨月需要点击两次或者更多）得到具有航班的日期，"""
        url = "http://m.flycua.com/h5/book/queryPriceCalendar.json"
        Now = datetime.datetime.now()
        # 查询时间段
        dayList = range(5, 30)
        self.dateList = map(lambda x: (
            Now + datetime.timedelta(days=x)).strftime('%Y-%m-%d'), dayList)

        for i in CodeList[1:3]:
            start = Now + datetime.timedelta(days=dayList[0])
            end = Now + datetime.timedelta(days=dayList[-1])
            searchDate = [start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')]
            if end.strftime("%Y-%m") == start.strftime("%Y-%m"):
                searchDate.pop()

            for j in searchDate:
                formdata = {'dstCity1': i.get("TO"),
                            'orgCity1': i.get("From"),
                            'depDate':  j}
                yield FormRequest(url, formdata=formdata, callback=self.parse_flight_date, dont_filter=True, meta=formdata)

    def parse_flight_date(self, response):
        """解析json数据解析出该航段具有航班的日期"""
        flight_date = json.loads(response.body)
        flight_date_list = filter(lambda dateStr: flight_date.get(
            "prices").get(dateStr, None) not in ["-", None], self.dateList)
        for depDate in flight_date_list:
            formdata = {'adultTravelers': '1',
                        'childTravelers': '0',
                        'dstCity1': response.meta.get("dstCity1"),
                        'infantTravelers': '0',
                        'orgCity1': response.meta.get("orgCity1"),
                        'queryTripType': 'OW',
                        'takeoffdate1': depDate,
                        'takeoffdate2': ''}
            yield FormRequest(self.url, formdata=formdata, callback=self.parse_flight_Data, dont_filter=True, meta=formdata)

    def parse_flight_Data(self, response):
        """解析出页面中的数据"""
        title = response.xpath("//title/text()").extract_first()
        if title == u"验证码":   #具有验证码的重发
            print title
            yield FormRequest(self.url, formdata=response.meta, callback=self.parse_flight_Data, dont_filter=True, meta=response.meta)
        elif title == u"错误提示": #没有航班（防止航班售完）
            print title, response.meta
        else:
            timeLine = ["2_hours_ago", "Within_2_hours", "arrive_late"]
            divFlights = response.xpath("//div[@class='flight-list-item']")
            for i, flight in enumerate(divFlights):
                flightNo = flight.xpath(
                    "div//div[@class='item-content-orgCity']/div[@class='flight-no']/text()").extract_first().encode("utf-8")
                depTime = flight.xpath(
                    "div//div[@class='item-content-orgCity']/div[@class='flight-orgTime']/text()").extract_first().strip().encode("utf-8")
                arrTime = flight.xpath(
                    "div//div[@class='item-content-orgCity']/div[@class='flight-orgTime alignLeft']/text()").extract_first().strip().encode("utf-8")
                try:
                    addTime = flight.xpath(
                        "div//div[@class='item-content-orgCity']/div[@class='flight-orgTime alignLeft']/div/text()").extract_first().strip()[1:].encode("utf-8")
                except Exception as e:
                    addTime = "0"
                depDate = datetime.datetime.strptime(
                    response.meta["takeoffdate1"], '%Y-%m-%d')
                arriveDate = depDate + datetime.timedelta(days=int(addTime))
                lowPrice = flight.xpath(
                    "div//div[@class='ticketStatusWrap']/div[@class='ticketStatusPrice']/text()").extract_first().strip()[1:].encode("utf-8")
                ticketNumMeg = flight.xpath(
                    "div//div[@class='ticketStatusWrap']/a[@class='ticketNum']/text()").extract_first().strip()
                ticketNumList = re.findall(
                    r"\d+", ticketNumMeg.encode("utf-8"))
                if len(ticketNumList) == 0:
                    if ticketNumMeg == u"座位不足":
                        break
                    ticketNum = "10+"
                else:
                    ticketNum = ticketNumList[0]

                flightListWraps = response.xpath(
                    "//div[@class='flightListWrap']")
                menu = flightListWraps[i]
                details = menu.xpath("div[@class='flightList-cabinsGp']")
                for j in details:
                    price = re.search(r".*?(\d+)", j.xpath(
                        "div[@class='cabinsGpTop']/div[@class='PositionPrice Common-FrontSize-L common-FrontColor']/text()").extract_first().strip()).group(1).encode("utf-8")
                    if price == lowPrice:
                        PositionType = j.xpath(
                            "div[@class='cabinsGpTop']/div[@class='PositionType Common-FrontSize-M']/text()").extract_first().strip().encode("utf-8")
                        try:
                            redprice = re.search(r".*?(\d+)", j.xpath(
                                "div[@class='cabinsGpDetail']/div[@class='cabinsGpDetailIcon']/span[5]/span/text()").extract_first().strip()).group(1)
                        except Exception as e:
                            redprice = u"0"
                        ticketBackMessage = j.xpath(
                            "div[@class='cabinsGpDetail']/div[@class='ticketBack']/span[1]/@onclick").extract_first()
                        icon = re.findall(r"\d+%", ticketBackMessage)
                        if len(icon) == 0:
                            Refunds = dict(
                                zip(timeLine, [u"100%", u"100%", u"100%"]))
                            Change = dict(
                                zip(timeLine, [u"100%", u"100%", u"100%"]))
                        elif len(icon) == 6:
                            Refunds = dict(zip(timeLine, icon[:3]))
                            Change = dict(zip(timeLine, icon[3:]))
                        else:
                            Refunds = dict(
                                zip(timeLine, [u"100%", u"100%", u"100%"]))
                            Change = dict(
                                zip(timeLine, [u"100%", u"100%", u"100%"]))
                            with open("takeBackError.html", "rb") as f:
                                f.write(response.body)
                        break

                items = LianhangItem()
                items["departure_date"] = depDate.strftime("%Y-%m-%d")
                items["departure_route"] = response.meta["orgCity1"]
                items["arrival_route"] = response.meta["dstCity1"]
                items["flight"] = flightNo[2:]
                items["departure_time"] = depTime
                items["arrival_time"] = arrTime
                items["red"] = redprice.encode("utf-8")
                items["ticket_price"] = lowPrice
                items["surplus"] = ticketNum
                items["pm_type"] = PositionType
                items["times"] = ""
                items["airway"] = "KN"
                items["scan_time"] = datetime.datetime.now(
                ).strftime("%Y-%m-%d %H:%M")
                items["departure_dates"] = "%s-%s" % (depDate.strftime(
                    "%Y/%m/%d"), arriveDate.strftime("%Y/%m/%d"))
                items["off_site"] = "%s/%s" % (Refunds["arrive_late"].encode(
                    "utf-8"), Refunds["arrive_late"].encode("utf-8"))
                items["before_takeoff_2"] = "%s/%s" % (Refunds["2_hours_ago"].encode(
                    "utf-8"), Change["2_hours_ago"].encode("utf-8"))
                items["take_off_2"] = "%s/%s" % (Refunds["Within_2_hours"].encode(
                    "utf-8"), Refunds["Within_2_hours"].encode("utf-8"))

                yield items
                
                url = ""   #url 将json数据传入其它机器对接，我没有访问数据库的权限，对接人搭建一个web服务器接手数据
                saveData = dict(items)
                saveData["timestamp"] = "12"  #测试
                saveData["nonce"] = "23"      #测试
                saveData["signature"] = hashlib.sha1("1223%s"%pubkey).hexdigest()  #对接时使用
                yield Request(url, method='POST',
                              body=json.dumps(saveData),
                              headers={'Content-Type': 'application/json', "flag": "not need proxies"}, callback=self.postSave, dont_filter=True, meta={"items": items})

    def postSave(self, response):
        print response.body
        yield response.meta["items"]
