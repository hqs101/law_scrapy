import pymysql
from lxml import etree


# 配置数据库
conn = pymysql.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    passwd='root',
    db='law_scrapy',
    use_unicode=True,
    charset='utf8'
)
# 连接数据库
cur = conn.cursor()
# 使用指定数据库
cur.execute("USE law_scrapy")

sql = 'select * from law_scrapy.web_settingitem'
cur.execute(sql)
results = cur.fetchall()
row = results[-1]


def html_parser(one_row):
    path = "D:\Tools\Git\myGit\law_scrapy\law\download\HTML\北京市水务局最新法规\北京市行政执法机关移送涉嫌犯罪案件工作办法.html"
    with open(path, 'rb') as f:
        html = f.read().decode('utf-8')
        # print(html)
        selector = etree.HTML(html)
        source = one_row[7]
        title = selector.xpath(one_row[5])[0]
        doc = selector.xpath(one_row[9])
        print(source)
        print(doc)
        print(title)
        store_data(title, doc, source)


# 将数据传递至数据库的web_lawnature表
def store_data(title, doc, source):
    try:
        # 执行MySQL语句，将参数插入数据库表的相应字段
        cur.execute(
            "INSERT IGNORE INTO web_lawnature (title, doc, source) VALUES"
            " (\"%s\", \"%s\", \"%s\")",
            (title, doc, source))
        cur.connection.commit()
    except Exception as e:
        print("出现异常：" + str(e))

if __name__ == '__main__':
    html_parser(row)
