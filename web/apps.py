from django.apps import AppConfig
from suit.apps import DjangoSuitConfig
from suit.menu import ParentItem, ChildItem


class WebConfig(DjangoSuitConfig):
    menu = (
        ParentItem('Users and Groups', children=[
            ChildItem(model='auth.user'),
            ChildItem(model='auth.group')
        ]),
        ParentItem('Scrapy', children=[
            ChildItem(model='web.lawnature'),
            ChildItem(model='web.settingitem')
        ]),
    )
