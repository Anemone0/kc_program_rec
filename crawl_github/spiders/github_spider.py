#!/usr/bin/env python
# coding=utf-8

# @file craw_github.py
# @brief craw_github
# @author x565178035,x565178035@126.com
# @version 1.0
# @date 2016-07-13 19:33

from scrapy.spiders import CrawlSpider
from scrapy.http import Request
from scrapy.selector import Selector
from crawl_github.items import *
from scrapy.utils.project import get_project_settings
import os.path

settings = get_project_settings()


class GithubSpider(CrawlSpider):
    """
    个人仓库 https://github.com/Shougo?tab=repositories
    个人star https://github.com/stars/Shougo
    Follower https://github.com/Shougo/followers
    下载url  https://codeload.github.com/Shougo/neosnippet.vim/zip/master
    """
    name = 'github_spider'
    start_urls = ['https://github.com/Shougo?tab=repositories&type=source']
    is_root = True

    def parse(self, response):
        '''source'''
        source_repos = response.xpath('//*[@id="user-repositories-list"]//li')
        base_url = 'https://github.com'
        user_name = response.url.split('/')[-1].split('?')[0]
        user_item = UserItem()
        for e_repo in source_repos:
            repo_name = e_repo.xpath('div/h3/a/text()').extract()[0].replace("\n", "").strip()
            repo_url = e_repo.xpath('div/h3/a/@href').extract()[0].replace("\n", "")
            star_url = base_url + repo_url + '/stargazers'
            print repo_name
            yield Request(star_url, self.parse_star)
            watch_url = base_url + repo_url + '/watchers'
            yield Request(watch_url, self.parse_watch)
            fork_url = base_url + repo_url + '/network/members'
            yield Request(fork_url, self.parse_fork)
            user_item['user_name'] = user_name
            user_item['repo_name'] = repo_name
            user_item['action'] = 10
            yield user_item

    def parse_star(self, response):
        base_url = 'https://github.com'
        users = response.xpath('//*[@id="repos"]/ol/li')
        repo_name = response.url.split('/')[-2]
        #  https://github.com/no13bus/ohmyrepo/stargazers
        user_item = UserItem()
        for each in users:
            #  user_name=each.xpath('div[2]/h3/span/a/text()').extract()[0].replace("\n","").strip()
            user_url = each.xpath('div[2]/h3/span/a/@href').extract()[0].replace("\n", "").strip()
            user_name = user_url[1:]
            user_url = base_url + user_url + '?tab=repositories&type=source'
            user_item['user_name'] = user_name
            user_item['repo_name'] = repo_name
            user_item['action'] = 1
            yield user_item
            yield Request(user_url, callback=self.parse)

    def parse_watch(self, response):
        base_url = 'https://github.com'
        users = response.xpath('//*[@id="repos"]/ol/li')
        repo_name = response.url.split('/')[-2]
        #  https://github.com/no13bus/ohmyrepo/stargazers
        user_item = UserItem()
        for each in users:
            #  user_name=each.xpath('div[2]/h3/span/a/text()').extract()[0].replace("\n","").strip()
            user_url = each.xpath('div[2]/h3/span/a/@href').extract()[0].replace("\n", "").strip()
            user_name = user_url[1:]
            user_url = base_url + user_url + '?tab=repositories&type=source'
            user_item['user_name'] = user_name
            user_item['repo_name'] = repo_name
            user_item['action'] = 3
            yield user_item
            yield Request(user_url, callback=self.parse)

    def parse_fork(self, response):
        base_url = 'https://github.com'
        users = response.xpath('//*[@id="network"]/div[@class="repo"]/a[1]/@href')
        repo_name = response.url.split('/')[-3]
        user_item = UserItem()
        for each in users:
            user_url = each.extract()
            user_name = user_url[1:]
            user_url = base_url + user_url + '?tab=repositories&type=source'
            print user_url
            user_item['user_name'] = user_name
            user_item['repo_name'] = repo_name
            user_item['action'] = 6
            yield user_item
            yield Request(user_url, callback=self.parse)
