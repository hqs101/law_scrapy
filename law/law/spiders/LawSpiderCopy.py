import os
import scrapy
from scrapy.http import Request
from law.items import UrlItem
import requests
from scrapy.exceptions import NotSupported
from scrapy.utils.project import get_project_settings
import pymysql


class LawSpider(scrapy.Spider):
    name = "lawCopy"
    allowed_domains = ['www.bjwater.gov.cn']

    def __init__(self, category=None, *args, **kwargs):
        super(LawSpider, self).__init__(*args, **kwargs)
        self.settings = get_project_settings()
        self.connect = pymysql.connect(
            host=self.settings['MYSQL_HOST'],
            db=self.settings['MYSQL_DBNAME'],
            user=self.settings['MYSQL_USER'],
            passwd=self.settings['MYSQL_PASSWD'],
            charset=self.settings['MYSQL_CHARSET'],
            use_unicode=True
        )
        self.cursor = self.connect.cursor(cursor=pymysql.cursors.DictCursor)

    def start_requests(self):
        sql = 'select * from law_scrapy.web_settingitem'
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        row = results[-1]
        yield Request(url=row['start_url'], meta={'row': row}, callback=self.get_this_urls)
        # for row in results:
        #     yield Request(url=row['start_url'], meta={'row': row}, callback=self.get_this_urls)

    def get_this_urls(self, response):
        row = response.meta['row']
        urls = response.xpath(row['target_url_xpath']).extract()    #提取页面条目列表url
        # print(urls)
        for url in urls:
            url = response.urljoin(url)
            try:
                item = UrlItem()
                item['url'] = response.urljoin(url)
                yield item
            except:
                pass

        print(response.xpath(row['nextpage_url_xpath']).extract()[0])
        next_page = response.xpath(row['nextpage_url_xpath']).extract()[0]
        if next_page != row['nextpage_end_condition']:
            print('nextpage---------' + next_page)
            next_url = response.urljoin(next_page)
            yield Request(url=next_url, meta={'row': row}, callback=self.get_this_urls)

    #下载html
    # def download_html(self, response):
    #     row = response.meta['row']
    #
    #     file_path = "download/HTML/"+str(row['title'])+"/"
    #     if not os.path.exists(file_path):
    #         os.makedirs(file_path)
    #     html_name = response.xpath(row['title_xpath']).extract()[0]
    #     print("-------------------------------------")
    #     print(response.url)
    #     print(html_name)
    #     print("-------------------------------------")
    #     with open(file_path + html_name + ".html", 'wb') as f:
    #         f.write(response.body)
