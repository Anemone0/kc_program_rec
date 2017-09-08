# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from scrapy.exporters import CsvItemExporter
from scrapy.utils.project import get_project_settings
from crawl_github.items import *
import os.path

settings = get_project_settings()
CSVDir = settings.get('CSV_DIR')


class MultiCSVItemPipeline(object):
    SaveTypes = ['UserItem', 'Repo']

    def __init__(self):
        dispatcher.connect(self.spider_opened, signal=signals.spider_opened)
        dispatcher.connect(self.spider_closed, signal=signals.spider_closed)

        self.files = dict([(name, open(os.path.join(CSVDir, name + '.csv'), 'w+b')) for name in self.SaveTypes])
        exporters = []
        for name in self.SaveTypes:
            exporters.append((name, \
                              CsvItemExporter(fields_to_export=globals()[name].fields.keys(),
                                              file=self.files[name])
                              ))
        self.exporters = dict(exporters)

        @classmethod
        def from_crawler(cls, crawler):
            pipeline = cls()
            crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
            crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
            return pipeline

    def spider_opened(self, spider):
        [e.start_exporting() for e in self.exporters.values()]

    def spider_closed(self, spider):
        [e.finish_exporting() for e in self.exporters.values()]
        [f.close() for f in self.files.values()]

    def process_item(self, item, spider):
        for each in self.exporters.keys():
            if isinstance(item, globals()[each]):
                self.exporters[each].export_item(item)
        return item
