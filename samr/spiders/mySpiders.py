# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
from scrapy.selector import Selector
from samr.util import pipelines


class Samr(scrapy.Spider):
    name = "samr"

    def __init__(self, qt=None, beginTime=None, batchNumber=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3904.17 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Host': 'www.samr.gov.cn',
            'Connection': 'Keep-Alive'
        }
        cookie = 'toolsStatus=1; SearchHistory=%25E5%258C%25BB%25E9%2599%25A2%252C; CPS_SESSION=6C80EABDD5982643DAE5A93A1DF7CDE4; SERVERID=5a6f3c6957c85e6635c3bc9baa5313c7|1571480253|1571480213; wwwcookie=20111111; __jsluid_h=6a31f43e2e43b309c901eb867ddf450e'

        self.ck = {item.split('=')[0]: item.split('=')[1] for item in cookie.split('; ')}
        self.qt = qt
        self.t = beginTime
        self.page = 0
        self.i = 1
        # 启动信息记录
        # self.batchNumber = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        self.batchNumber = batchNumber
        startTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        beginTime = self.t
        afterTime = datetime.datetime.now().strftime('%Y-%m-%d')
        item = {}
        item.update(table='info')
        item.update(batchNumber=self.batchNumber)
        item.update(startTime=startTime)
        item.update(beginTime=beginTime)
        item.update(afterTime=afterTime)
        item.update(flag=0)
        item.update(qt=qt)
        pipelines.process_item(item)

    def start_requests(self):
        url = "http://www.samr.gov.cn/so/s?x=0&y=0&token=849&qt=" + self.qt + "&tab=all&siteCode=bm30000012&toolsStatus=1&sort=dateDesc"
        yield scrapy.Request(
            url=url,
            method='GET',
            callback=self.parse1,
            dont_filter=True,
            cookies=self.ck,
            headers=self.headers
        )

    def parse1(self, response):
        text = response.body.decode()
        nums = int(str(re.findall(r'相关结果(.*?)个', text, re.S)[0]).replace(' ', ''))
        print(nums)
        if nums % 10 == 0:
            pages = nums // 10
        else:
            pages = nums // 10 + 1
        self.page = pages

        url = "http://www.samr.gov.cn/so/s?x=0&y=0&token=849&qt=" + self.qt + "&tab=all&siteCode=bm30000012&toolsStatus=1&sort=dateDesc&page=" + str(
            self.i)
        yield scrapy.Request(
            url=url,
            method='GET',
            callback=self.parse2,
            dont_filter=True,
            cookies=self.ck,
            headers=self.headers
        )

    def parse2(self, response):
        text = response.body.decode()
        items = Selector(text=text).css(".news").extract()
        if items == [] or len(items) == 1:
            items = Selector(text=text).css(".discuss").extract()
        try:
            # del items[0]
            # del items[0]

            for item in items:
                tag = re.findall(r'<span.*?>(.*?)</span>', item)
                if tag:
                    tag = tag[0]
                    tagAs = re.findall(r'<a.*?>(.*?)</a>', item, re.S)
                    # 去除标签符号
                    acon = re.compile(r'<[^>]+>', re.S)
                    title = acon.sub('', tagAs[0]).replace('\r', '').replace('\n', '').replace(' ', '')
                    releaseTime = re.findall(r'(\d{4}-\d{2}-\d{2})', item)[0]
                    if releaseTime > self.t:
                        url = 'http://www.samr.gov.cn/so/' + str(re.findall(r'<a href="(.*?)"', item, re.S)[0]).replace(
                            ';', '&')
                        yield scrapy.Request(
                            url=url,
                            method='GET',
                            callback=self.parse3,
                            dont_filter=True,
                            cookies=self.ck,
                            headers=self.headers,
                            meta={
                                'tag': tag,
                                'title': title,
                                'releaseTime': releaseTime
                            }
                        )
                        # print(tag, title, releaseTime, url)
                    else:
                        return

                else:
                    continue

                self.i += 1
                if self.i <= self.page:
                    nexturl = "http://www.samr.gov.cn/so/s?x=0&y=0&token=849&qt=" + self.qt + "&tab=all&siteCode=bm30000012&toolsStatus=1&sort=dateDesc&page=" + str(
                        self.i)
                    yield scrapy.Request(
                        url=nexturl,
                        method='GET',
                        callback=self.parse2,
                        dont_filter=True,
                        cookies=self.ck,
                        headers=self.headers
                    )
        except Exception as e:
            # print(e)
            yield scrapy.Request(
                url=response.url,
                method='GET',
                callback=self.parse2,
                dont_filter=True,
                cookies=self.ck,
                headers=self.headers
            )

    def parse3(self, response):
        tag = response.meta['tag']
        title = response.meta['title']
        releaseTime = response.meta['releaseTime']
        text = response.body.decode()
        url = re.findall(r'location.href = "(.*?)"', text)[0]

        yield scrapy.Request(
            url=url,
            method='GET',
            callback=self.parse4,
            dont_filter=True,
            cookies=self.ck,
            headers=self.headers,
            meta={
                'tag': tag,
                'title': title,
                'releaseTime': releaseTime,
                'url': url
            }
        )

    def parse4(self, response):
        item = {}
        tag = response.meta['tag'].strip()
        title = response.meta['title']
        releaseTime = response.meta['releaseTime']
        url = response.meta['url']
        flag = False
        if '.pdf' == str(response.url)[-4:]:
            flag = True
        else:
            text = response.body.decode()

        if flag:
            content = 'PDF文件暂未处理'

        elif tag == '服务':
            content = Selector(text=text).css(".Three_xilan_07").extract()
            # 去除标签
            acon = re.compile(r'<[^>]+>', re.S)
            content = acon.sub('', content[0]).replace('\r', '').replace('\n', '').replace(' ', '').replace('  ', ';')


        # elif tag == '新闻' or tag == '司局动态' or tag == '反不正当竞争' or tag == '质量提升行动':
        else:
            content = Selector(text=text).css(".TRS_Editor").extract()
            # 去除标签
            acon = re.compile(r'<[^>]+>', re.S)
            try:
                content = acon.sub('', content[0]).replace('\r', '').replace('\n', '').replace('.TRS_Editor', '').replace(',P{font-family:宋体;}', '').replace('{font-family:宋体;}', '').replace(' ', '').replace(',P', '').replace(',p', '').strip()
            except:
                content = ''
        # print(tag, title, releaseTime, url, content)
        item.update(table='content')
        item.update(tag=tag)
        item.update(title=title)
        item.update(releaseTime=releaseTime)
        item.update(url=url)
        item.update(content=content)
        item.update(updateTime=datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S'))
        item.update(batchNumber=self.batchNumber)
        item.update(qt=self.qt)
        pipelines.process_item(item)
        # input('=================')
