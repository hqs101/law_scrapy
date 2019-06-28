import os
import scrapy
from scrapy.http import Request
from law.items import LawItem
import requests
from scrapy.exceptions import NotSupported
from scrapy.utils.project import get_project_settings
import pymysql


class LawAnalysis(scrapy.Spider):
    name = "analysis"
    allowed_domains = ['www.bjwater.gov.cn']

    def __init__(self, category=None, *args, **kwargs):
        super(LawAnalysis, self).__init__(*args, **kwargs)
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

        sql_urls = 'select * from law_scrapy.web_lawurl'
        self.cursor.execute(sql_urls)
        url_results = self.cursor.fetchall()
        for sql_url in url_results:
            try:
                yield Request(url=sql_url['url'], meta={'row': row}, callback=self.get_info)
            except:
                pass

        delete_urls = 'delete from law_scrapy.web_lawurl'
        self.cursor.execute(delete_urls)

    def get_info(self, response):
        url = response.url
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

            item['title'] = title
            item['doc'] = doc
            item['url'] = response.urljoin(url)
            yield item
        except NotSupported as e:
            self.download_file(response, url)
        except:
            pass

    def download_file(self, response, url):
        row = response.meta['row']
        try:
            file_path = "download/附件/" + str(row['title']) + "/"
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            print("-------------------------------------")
            print(response.url)
            print("-------------------------------------")

            file_name = url.split('/')[-1]
            response = requests.get(url)
            f = open(file_path + file_name, "wb")
            for chunk in response.iter_content(chunk_size=512):
                if chunk:
                    f.write(chunk)
            print('保存文件: %s' % file_name)
        except:
            print('error')
