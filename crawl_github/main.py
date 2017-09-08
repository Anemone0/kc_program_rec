#!/usr/bin/env python
#coding=utf-8

# @file main.py
# @brief main
# @author x565178035,x565178035@126.com
# @version 1.0
# @date 2016-07-13 16:06

import os

def main():
    #  os.system( "scrapy crawl github_spider -L WARNING" )
    os.system("scrapy crawl github_spider_ol")

if __name__ == '__main__':
    main()

