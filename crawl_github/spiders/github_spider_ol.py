#!/usr/bin/env python
# coding=utf-8

# @file craw_github.py
# @brief 杂志版, 包含watch的抓取,以及自动生成readme和sourcecode文件
# @author x565178035,x565178035@126.com
# @version 1.0
# @date 2016-07-13 19:33
import logging

from scrapy.spiders import CrawlSpider
from scrapy.http import Request
from scrapy.selector import Selector
from twisted.internet.defer import CancelledError

from crawl_github.items import *
from scrapy.utils.project import get_project_settings
import os.path
import executezip
import zipfile

PYTHON_FILE_PATH = os.path.split(os.path.realpath(__file__))[0]
settings = get_project_settings()
ZIP_DIR = os.path.join(PYTHON_FILE_PATH, "..", "zip")

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
    start_urls = ['https://github.com/eastridge?tab=repositories']

    def parse(self, response, step=0):

        logging.info(response)
        person = response.meta.get('person', 0)
        if response.meta.has_key('step'):
            step = response.meta['step']
        else:
            step = 0
        if step >= 2:
            return
        # if person>=10:
        #     return

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
                repo_url = user_name + "/" + repo_name
                star_url = base_url + repo_url + '/stargazers'
                fork_url = base_url + repo_url + '/network/members'
                yield Request(base_url + "/" + repo_url, callback=self.parse_repo)
                watch_url = base_url + '/' + repo_url + '/watchers'
                yield Request(watch_url, meta={"step": step}, callback=self.parse_watch)
            '''fork'''
            fork_repos = response.xpath('//li[contains(@class,"fork")]')
            for e_repo in fork_repos:
                repo_name = e_repo.xpath('div/h3/a/text()').extract()[0].replace("\n", "").strip()
                repo_owner = e_repo.xpath('div/span/a/@href').extract()[0].split('/')[1]
                user_item['user_name'] = user_name
                user_item['repo_name'] = repo_owner + '/' + repo_name
                user_item['action'] = 6
                yield user_item
                owner_index = base_url + "/" + repo_owner + "?tab=repositories"
                person += 1
                yield Request(owner_index, meta={"step": step + 1, "person": person}, callback=self.parse)

                repo_url = e_repo.xpath('div/span/a/@href').extract()[0]. \
                    replace("\n", "")
                # yield Request(base_url + repo_url, callback=self.parse_repo)

            next_url = response.xpath('//a[contains(@class,"next_page")]/@href').extract()
            if len(next_url) >= 1:
                yield Request(base_url + next_url[0], meta={"step": step, "person": person}, callback=self.parse)
            else:
                '''started'''
                yield Request(base_url + "/stars/" + user_name, meta={"step": step}, callback=self.parse_star)

    def parse_watch(self, response):
        person = response.meta.get('person', 0)
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
            person += 1
            # yield Request(user_url, meta={"step": response.meta['step'] + 1}, callback=self.parse)

    def parse_star(self, response):
        person = response.meta.get('person', 0)
        user_name = response.url.split('/')[-1].split('?')[0]
        star_repos = response.xpath('//ul[contains(@class,"repo-list")]/li')
        base_url = 'https://github.com'
        user_item = UserItem()
        for e_repo in star_repos:
            repo_owner, repo_name = e_repo.xpath('div/h3/a/@href').extract()[0].split('/')[1:]

            if repo_owner != user_name:
                user_item['user_name'] = user_name
                user_item['repo_name'] = repo_owner + '/' + repo_name
                user_item['action'] = 1
                yield user_item
                owner_index = base_url + "/" + repo_owner + "?tab=repositories"
                person += 1
                yield Request(owner_index, meta={"step": response.meta['step'] + 1, "person": person},
                              callback=self.parse)
                repo_url = e_repo.xpath('div/h3/a/@href').extract()[0]. \
                    replace("\n", "")
                # yield Request(base_url + repo_url, callback=self.parse_repo)

        next_url = response.xpath('//a[contains(text(),"Next")]/@href').extract()
        if len(next_url) >= 1:
            yield Request(next_url[0], meta={"step": response.meta['step'] + 1, "person": person},
                          callback=self.parse_star)



    def parse_repo(self, response):
        repo = Repo()
        xpath_name = '//*[@id="js-repo-pjax-container"]/div[1]/div[1]/h1/strong/a/text()'
        xpath_desc = '//span[contains(@itemprop,"about")]/text()'
        xpath_download_url = '//a[contains(@data-ga-click,"download")]/@href'
        xpath_lang = '//span[contains(@class,"lang")]/text()'
        repo['name'] = response.xpath(xpath_name).extract()[0]
        try:
            repo['description'] = response.xpath(xpath_desc).extract()[0].strip()
        except IndexError:
            repo['description'] = 'None'

        repo['language'] = "|".join(response.xpath(xpath_lang).extract())
        repo['url'] = response.url

        repo_readme = RepoReadme()
        repo_source = RepoSource()
        zip_url = base_url + response.xpath(xpath_download_url).extract()[0]
        file_name = response.url.split('/')[4]
        path = os.path.join(ZIP_DIR, file_name + '.zip')
        try:
            zipfile.ZipFile(path, 'r')
            readme, source = executezip.analyse(path)
            repo_readme = RepoReadme()
            repo_readme['name'] = file_name
            repo_readme['readme'] = readme
            yield repo_readme
            repo_source = RepoSource()
            repo_source['name'] = file_name
            repo_source['source'] = source
            yield repo_source
        except Exception:
            try:
                yield Request(zip_url, callback=self.save_repo)
            except CancelledError:
                repo_readme = RepoReadme()
                repo_readme['name'] = file_name
                repo_readme['readme'] = '0'
                yield repo_readme
                repo_source = RepoSource()
                repo_source['name'] = file_name
                repo_source['source'] = '0'
                yield repo_source

        yield repo

    def save_repo(self, response):
        logging.info(response)
        file_name = response.url.split('/')[4]
        path = os.path.join(ZIP_DIR, file_name + '.zip')

        with open(path, 'wb') as f:
            f.write(response.body)
        readme, source = executezip.analyse(path)
        repo_readme = RepoReadme()
        repo_readme['name'] = file_name
        repo_readme['readme'] = readme
        yield repo_readme
        repo_source = RepoSource()
        repo_source['name'] = file_name
        repo_source['source'] = source
        yield repo_source
        # print readme, source
