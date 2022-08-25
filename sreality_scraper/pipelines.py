# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient

class SaveToDbPipeline:

    collection_name = 'houses'


    def open_spider(self, spider):

        self.ids_seen = set()
        self.client = MongoClient(host= spider.settings.get("MONGODB_HOST"))
        self.db = self.client[ spider.settings.get("MONGODB_DB")]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(dict(item))
        return item
