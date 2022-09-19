# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from datetime import datetime
import certifi
from pymongo import MongoClient, InsertOne,  ReplaceOne

class SaveToDbPipeline:

    collection_name = 'houses'

    batch_size = 1000

    def open_spider(self, spider):
        self.spider = spider
        self.client = MongoClient(spider.settings.get("MONGODB_CONNECTION_STRING"), tlsCAFile=certifi.where())
        self.db = self.client[spider.settings.get("MONGODB_DB")]
        self.coll = self.db[self.collection_name]
        self.date = datetime.now()
        self.datestr = self.date.strftime('%Y-%m-%d')

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
        if 'updateHistory' not in item:         
            item['updateHistory'] = {}


        if old_item['price'] != item['price']:
            item['priceHistory'][self.datestr] = item['price']
            item['updateHistory'][self.datestr] = 2
        item['lastUpdate'] = self.datestr

        first_price = item['priceHistory'].values()[0]
        item['priceDrop'] = (first_price - item['price'] ) / first_price 

        first_date = datetime.strptime(item['priceHistory'].keys()[0], '%Y-%m-%d')
        item['age'] = (self.date - first_date).days

        self.buffer.append(ReplaceOne({'_id': old_item['_id']}, item))

    def insert(self, item):

        item['priceHistory'] = {
            self.datestr: item['price']
        }
        item['updateHistory'] = {
            self.datestr: 1
        }
        item['lastUpdate'] = self.datestr
        item['priceDrop'] = 0
        item['age'] = 0

        self.buffer.append(InsertOne(item))


    def flush_buffer(self, force=False):
        if len(self.buffer) >= self.batch_size or (force and len(self.buffer) > 0):
            
            self.coll.bulk_write(self.buffer)
            self.buffer = []
            self.buffer_size = 0
            self.spider.logger.info(f'Saved {self.item_counter} items')

    
