import os

import scrapy
from scrapy.http import Request
from law.items import LawItem
import requests
import re
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
        for row in results:
            yield Request(url=row['start_url'], meta={'row': row}, callback=self.get_this_urls)

    def parse(self, response):
        row = response.meta['row']
        category_urls = response.xpath(row['law_url_xpath']).extract()  #最新法规
        policy_url = response.xpath(row['policy_url_xpath']).extract()  #政策解读
        plan_url = response.xpath(row['plan_url_xpath']).extract()  #规划计划总结
        category_urls.append(policy_url[0])
        category_urls.append(plan_url[0])
        for category_url in category_urls:
            url = response.urljoin(category_url)
            yield Request(url=url, meta={'row': row}, callback=self.get_this_urls)

    def get_this_urls(self, response):
        row = response.meta['row']
        urls = response.xpath(row['target_url_xpath']).extract()    #提取页面条目列表url
        # print(urls)
        for url in urls:
            url = response.urljoin(url)
            yield Request(url=url, meta={'url': url, 'row': row}, callback=self.parse_item)

        next_page = response.xpath(row['nextpage_url_xpath']).extract()[0]
        if next_page != row['nextpage_end_condition']:
            print('nextpage---------' + next_page)
            next_url = response.urljoin(next_page)
            yield Request(url=next_url, meta={'row': row}, callback=self.get_this_urls)

    def parse_item(self, response):
        row = response.meta['row']

        file_path = "download/HTML/"+str(row['title'])+"/"
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        html_name = response.xpath(row['title_xpath']).extract()[0]
        print("-------------------------------------")
        print(response.url)
        print(html_name)
        print("-------------------------------------")
        with open(file_path + html_name + ".html", 'wb') as f:
            f.write(response.body)

    def get_info(self, response):
        url = response.meta['url']
        row = response.meta['row']
        try:
            # 处理附件
            urls = response.xpath(row['appendix_xpath']).extract()
            for file_url in urls:
                print('处理附件......')
                file_url = response.urljoin(file_url)
                print('文件url:'+file_url)
                self.download_file(response, file_url)

            item = LawItem()
            title = response.xpath(row['title_xpath']).extract()[0]
            # divs = response.xpath(row['doc_div_xpath'])
            doc = response.xpath(row['doc_div_xpath']).extract()
            # for p in divs.xpath(row['dov_xpath']):
            #     doc += p.extract().strip()

            item['title'] = title
            item['doc'] = doc
            item['url'] = response.urljoin(url)
            yield item
        except NotSupported as e:
            self.download_file(response, url)
        except:
            pass

    def download_file(self, response, url):
        try:
            file_name = url.split('/')[-1]
            response = requests.get(url)
            f = open("download/" + file_name, "wb")
            for chunk in response.iter_content(chunk_size=512):
                if chunk:
                    f.write(chunk)
            print('保存文件: %s' % file_name)
        except:
            print('error')
