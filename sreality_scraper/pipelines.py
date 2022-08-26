# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from datetime import datetime
from itemadapter import ItemAdapter
from pymongo import MongoClient, InsertOne,  ReplaceOne

class SaveToDbPipeline:

    collection_name = 'houses'

    batch_size = 1000

    def open_spider(self, spider):
        self.spider = spider
        self.client = MongoClient(host= spider.settings.get("MONGODB_HOST"))
        self.db = self.client[ spider.settings.get("MONGODB_DB")]
        self.coll = self.db[self.collection_name]
        self.date = str(datetime.now())

        self.buffer = []
        self.item_counter = 1



    def close_spider(self, spider):
        self.flush_buffer(force=True)
        self.client.close()

    def process_item(self, item, spider):
        current = self.coll.find_one({'id': item['id']})

        if current is None:
            self.insert(dict(item))
        else:
            self.update(dict(item), current)

        
        self.flush_buffer()
        self.item_counter += 1

        return item

    def update(self, item, old_item):
        item['priceHistory'] = old_item['priceHistory']
        item['priceHistory'][self.date] = item['price']
        item['lastUpdate'] = self.date

        self.buffer.append(ReplaceOne({'_id': old_item['_id']}, item))

    def insert(self, item):

        item['priceHistory'] = {
            self.date: item['price']
        }
        item['lastUpdate'] = self.date

        self.buffer.append(InsertOne(item))


    def flush_buffer(self, force=False):
        if len(self.buffer) >= self.batch_size or (force and len(self.buffer) > 0):
            
            self.coll.bulk_write(self.buffer)
            self.buffer = []
            self.buffer_size = 0
            self.spider.logger.info(f'Saved {self.item_counter} items')

    
