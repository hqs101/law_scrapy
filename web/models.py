from django.db import models

# Create your models here.


class LawNature(models.Model):
    source = models.CharField(max_length=1000, verbose_name='来源')
    title = models.CharField(max_length=1000, verbose_name='标题')
    doc = models.TextField(verbose_name='内容')

    def __str__(self):
        return self.title

    # class Meta:
    #     unique_together = ('url', )


class SettingItem(models.Model):
    title = models.CharField(max_length=200, verbose_name='爬虫名称')
    allowed_domains = models.CharField(max_length=200, verbose_name='URL过滤', help_text='主机名不符合该项的URL将会被拦截')
    start_url = models.CharField(max_length=1000, verbose_name='起始URL')

    # policy_url_xpath = models.CharField(max_length=200, verbose_name='政策解读 Xpath')
    # plan_url_xpath = models.CharField(max_length=200, verbose_name='规划计划 Xpath')
    # law_url_xpath = models.CharField(max_length=200, verbose_name='法律法规 Xpath')

    target_url_xpath = models.CharField(max_length=200, verbose_name='爬取列表 Xpath')
    nextpage_url_xpath = models.CharField(max_length=200, verbose_name='下一页 Xpath')
    nextpage_end_condition = models.CharField(max_length=200, verbose_name='下一页存在判断条件')

    title_xpath = models.CharField(max_length=200, verbose_name='标题 Xpath')
    doc_div_xpath = models.CharField(max_length=200, verbose_name='正文 Xpath')
    # dov_xpath = models.CharField(max_length=200, verbose_name='正文 Xpath')
    appendix_xpath = models.CharField(max_length=200, verbose_name='附件 Xpath')

    def __str__(self):
        return self.title + '    ' + self.start_url
