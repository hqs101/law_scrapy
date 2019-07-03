import os
import scrapy
from scrapy.http import Request
import requests
from scrapy.utils.project import get_project_settings
import pymysql
from lxml import etree


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

    # --------------------------------------------------------------------- 爬取开始
    def start_requests(self):
        sql = 'select * from law_scrapy.web_settingitem'
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        row = results[-1]
        yield Request(url=row['start_url'], meta={'row': row}, callback=self.get_urls)
        # for row in results:
        #     yield Request(url=row['start_url'], meta={'row': row}, callback=self.get_this_urls)

    def get_urls(self, response):
        row = response.meta['row']
        urls = response.xpath(row['target_url_xpath']).extract()    #提取页面列表url
        # print(urls)
        for url in urls:
            url = response.urljoin(url)
            try:
                yield Request(url=url, meta={'row': row}, callback=self.download_html)
            except Exception as e:
                print(Exception, ":", e)

        # print(response.xpath(row['nextpage_url_xpath']).extract()[0])
        next_page = response.xpath(row['nextpage_url_xpath']).extract()[0]
        if next_page != row['nextpage_end_condition']:
            print('nextpage---------' + next_page)
            next_url = response.urljoin(next_page)
            yield Request(url=next_url, meta={'row': row}, callback=self.get_urls)

    # 下载html/pdf
    def download_html(self, response):
        row = response.meta['row']
        file_path = "download/HTML/"+str(row['title'])+"/"
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        try:
            html_name = response.xpath(row['title_xpath']).extract()[0]
            with open(file_path + html_name + ".html", 'wb') as f:
                f.write(response.body)
            print("-------------------------------------")
            print("已保存HTML : "+html_name)
            print("-------------------------------------")
            try:
                self.get_appendix(response)
                self.html_parser(row, file_path + html_name + ".html")
            except Exception as e:
                print(Exception, ":", e)
        except:
            url = response.url
            file_name = url.split('/')[-1]
            response = requests.get(url)
            f = open(file_path + file_name, "wb")
            for chunk in response.iter_content(chunk_size=512):
                if chunk:
                    f.write(chunk)
            print("-------------------------------------")
            print("已保存PDF : " + file_name)
            print("-------------------------------------")

    # --------------------------------------------------------------------- 解析函数
    def html_parser(self, row, file_path):
        # 本地HTML文件路径
        path = "D:/Tools/Git/myGit/law_scrapy/law/" + file_path
        with open(path, 'rb') as f:
            html = f.read().decode('utf-8')
            # print(html)
            selector = etree.HTML(html)
            source = row['title']
            title = selector.xpath(row['title_xpath'])[0]
            doc = selector.xpath(row['doc_div_xpath'])
            self.store_data(title, doc, source)

    # 查找附件
    def get_appendix(self, response):
        row = response.meta['row']
        try:
            urls = response.xpath(row['appendix_xpath']).extract()
            for file_url in urls:
                print('处理附件......')
                file_url = response.urljoin(file_url)
                print('附件URL:'+file_url)
                self.download_file(response, file_url)
        except Exception as e:
            print("查找附件时异常：" + str(e))

    # 下载附件
    def download_file(self, response, url):
        row = response.meta['row']
        try:
            # file_path = "download/附件/" + str(row['title']) + "/"
            file_path = "download/附件/" + str(row['title']) + "/"
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            print("-------------------------------------")
            print(response.url)
            print("-------------------------------------")

            file_name = response.xpath(row['title_xpath']).extract()[0] + url.split('/')[-1]
            response = requests.get(url)
            f = open(file_path + file_name, "wb")
            for chunk in response.iter_content(chunk_size=512):
                if chunk:
                    f.write(chunk)
            print('保存文件: %s' % file_name)
        except:
            pass

    # 将数据传递至数据库的web_lawnature表
    def store_data(self, title, doc, source):
        try:
            # 执行MySQL语句，将参数插入数据库表的相应字段
            self.cursor.execute(
                "INSERT IGNORE INTO web_lawnature (title, doc, source) VALUES"
                " (\"%s\", \"%s\", \"%s\")",
                (title, doc, source))
            self.cursor.connection.commit()
            print("---------------新增一条数据----------------")
        except Exception as e:
            print("数据存库异常：" + str(e))


