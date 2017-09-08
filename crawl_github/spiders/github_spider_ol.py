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
ZIP_DIR = "./zip"

base_url = 'https://github.com'

class GithubSpider(CrawlSpider):
    """
    个人仓库 https://github.com/Shougo?tab=repositories
    个人star https://github.com/stars/Shougo
    Follower https://github.com/Shougo/followers
    下载url  https://codeload.github.com/Shougo/neosnippet.vim/zip/master
    """
    name = 'github_spider_ol'

    #  start_urls=['https://github.com/shougo?tab=repositories']
    #  start_urls=['https://github.com/nicolaiarocci?tab=repositories']
    #  start_urls=['https://github.com/allofthenorthwood?tab=repositories']
    start_urls = ['https://github.com/carpedm20?tab=repositories']

    def parse(self, response, step=0):
        if response.meta.has_key('step'):
            step = response.meta['step']
        else:
            step = 0
        if step >= 1:
            return
        '''source'''
        source_repos = response.xpath('//li[contains(@class,"source")]')
        email = None
        user_name = response.url.split('/')[-1].split('?')[0]
        base_url = 'https://github.com'
        user_item = UserItem()
        try:
            email = response.xpath('//*[@id="js-pjax-container"]//li[@aria-label="Email"]/a/text()').extract()[0]
        except Exception, e:
            pass

        if email or True:
            for e_repo in source_repos:
                repo_name = e_repo.xpath('div/h3/a/text()').extract()[0].replace("\n", "").strip()
                user_item['user_name'] = user_name
                user_item['repo_name'] = user_name + '/' + repo_name
                user_item['action'] = 10
                yield user_item

                repo_url = e_repo.xpath('//a[contains(@itemprop, "name codeRepository")]/@href').extract()[0].replace(
                    "\n", "")
                star_url = base_url + repo_url + '/stargazers'
                # print repo_name
                fork_url = base_url + repo_url + '/network/members'

                watch_url = base_url + repo_url + '/watchers'

                yield Request(base_url + repo_url, callback=self.parse_repo)

                # yield Request(watch_url, meta={"step": step}, callback=self.parse_watch)
        #     '''fork'''
        #     fork_repos = response.xpath('//li[contains(@class,"fork")]')
        #     for e_repo in fork_repos:
        #         repo_name = e_repo.xpath('div/h3/a/text()').extract()[0].replace("\n", "").strip()
        #         repo_owner = e_repo.xpath('div/span/a/@href').extract()[0].split('/')[1]
        #         user_item['user_name'] = user_name
        #         user_item['repo_name'] = repo_owner + '/' + repo_name
        #         user_item['action'] = 6
        #         yield user_item
        #         owner_index = base_url + "/" + repo_owner + "?tab=repositories"
        #         yield Request(owner_index, meta={"step": step + 1}, callback=self.parse)
        #
        #         repo_url = e_repo.xpath('//a[contains(@itemprop, "name codeRepository")]/@href').extract()[0].\
        #             replace("\n", "")
        #         yield Request(base_url + repo_url, callback=self.parse_repo)
        #
        #     '''started'''
        #     yield Request(base_url + "/stars/" + user_name, meta={"step": step}, callback=self.parse_star)
        #
        # next_url = response.xpath('//a[contains(@class,"next_page")]/@href').extract()
        # if len(next_url) >= 1:
        #     yield Request(base_url + next_url[0], meta={"step": step}, callback=self.parse)

    def parse_watch(self, response):
        users = response.xpath('//*[@id="repos"]/ol/li')
        repo_name = response.url.split('/')[-2]
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
            yield Request(user_url, meta={"step": response.meta['step'] + 1}, callback=self.parse)

    def parse_star(self, response):
        user_name = response.url.split('/')[-1]
        star_repos = response.xpath('//ul[@id="js-repo-list"]/li')
        base_url = 'https://github.com'
        user_item = UserItem()
        for e_repo in star_repos:
            repo_owner, repo_name = e_repo.xpath('div/h3/a/@href').extract()[0].split('/')[1:]

            user_item['user_name'] = user_name
            user_item['repo_name'] = repo_owner + '/' + repo_name
            user_item['action'] = 1
            yield user_item
            owner_index = base_url + "/" + repo_owner + "?tab=repositories"
            yield Request(owner_index, meta={"step": response.meta['step'] + 1}, callback=self.parse)
            repo_url = e_repo.xpath('//a[contains(@itemprop, "name codeRepository")]/@href').extract()[0].\
                    replace("\n", "")
            yield Request(base_url + repo_url, callback=self.parse_repo)

    def parse_repo(self, response):
        print response.url
        repo = Repo()
        xpath_name = '//*[@id="js-repo-pjax-container"]/div[1]/div[1]/h1/strong/a/text()'
        xpath_desc = '//span[contains(@itemprop,"about")]/text()'
        xpath_download_url='//a[contains(@data-ga-click,"download")]/@href'
        repo['name'] = response.xpath(xpath_name).extract()[0]
        repo['description'] = response.xpath(xpath_desc).extract()[0].strip()
        repo['url'] = response.url
        zip_url = base_url+response.xpath(xpath_download_url).extract()[0]
        yield Request(zip_url, callback=self.save_repo)
        yield repo

    def save_repo(self, response):
        file_name = response.url.split('/')[4]
        with open(os.path.join(ZIP_DIR, file_name + '.zip'), 'wb') as f:
            f.write(response.body)
