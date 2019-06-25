# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-06-24 08:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_auto_20190624_0810'),
    ]

    operations = [
        migrations.CreateModel(
            name='SettingItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_url', models.CharField(max_length=1000, verbose_name='起始URL')),
                ('policy_url_xpath', models.CharField(max_length=200, verbose_name='政策解读 Xpath')),
                ('plan_url_xpath', models.CharField(max_length=200, verbose_name='规划计划 Xpath')),
                ('law_url_xpath', models.CharField(max_length=200, verbose_name='法律法规 Xpath')),
                ('target_url_xpath', models.CharField(max_length=200, verbose_name='莫表页面 Xpath')),
                ('nextpage_url_xpath', models.CharField(max_length=200, verbose_name='下一页 Xpath')),
                ('nextpage_end_condition', models.CharField(max_length=200, verbose_name='下一页存在判断条件')),
                ('title_xpath', models.CharField(max_length=200, verbose_name='Title Xpath')),
                ('doc_xpath', models.CharField(max_length=200, verbose_name='正文 Xpath')),
                ('appendix_xpath', models.CharField(max_length=200, verbose_name='附件 Xpath')),
            ],
        ),
    ]
