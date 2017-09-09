# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import *


class Repo(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = Field()
    language = Field()
    description = Field()
    url = Field()


class UserItem(Item):
    user_name = Field()
    repo_name = Field()
    action = Field()


class RepoReadme(Item):
    name = Field()
    readme = Field()


class RepoSource(Item):
    name = Field()
    source = Field()
