# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from datetime import datetime, timedelta
# import certifi
from scrapy import Request
from pymongo import MongoClient, InsertOne,  ReplaceOne
from sreality_scraper.src.smapy import get_reverse_geocode_url, parse_reverse_geocode_xml
from sreality_scraper.src.utils import parse_int, get_area_from_listing
from sreality_scraper.src.sreality import property_codes

class SaveToDbPipeline:

    batch_size = 1000
    delete_threshold = 20000

    def __init__(self, crawler):
        self.crawler = crawler
        self.buffer = []
        self.insert_counter = 0
        self.update_counter = 0


    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def open_spider(self, spider):
        self.spider = spider
        self.client = MongoClient(spider.settings.get("MONGODB_CONNECTION_STRING"))
        db = self.client[spider.settings.get("MONGODB_DB")]
        self.collection = db[spider.settings.get("MONGODB_COLLECTION")]
        self.datestr = datetime.now().strftime('%Y-%m-%d')


    def close_spider(self, spider):
        self.flush_buffer(force=True)
        spider.logger.info(f'Inserted {self.insert_counter} items')
        spider.logger.info(f'Updated {self.update_counter} items')
        res = self.collection.update_many({'lastUpdate': self.datestr}, {'$unset': {'deleted': ""}})
        spider.logger.info(f'Restored {res.modified_count} items')   

        if self.update_counter > self.delete_threshold:
            res = self.collection.update_many({'lastUpdate': {'$ne': self.datestr}, 'deleted': {'$exists': False}}, {'$set': {'deleted': self.datestr}})
            spider.logger.info(f'Deleted {res.modified_count} items')     

        
        self.client.close()

    def process_item(self, item, spider):
        current = self.collection.find_one({'id': item['id']})

        item = dict(item)

        if 'pricePerMeter' not in item and 'price' in item:
            area, source = get_area_from_listing(item)
            if area:
                item['pricePerMeter'] = int(item['price'] / area)
                item['pricePerMeterSource'] = source

        if current is None:
            self.insert(item)
        else:
            self.update(item, current)

        self.flush_buffer()
        return item


    def update(self, item, old_item):
        self.update_counter += 1

        item['priceHistory'] = old_item['priceHistory']
        item['lastUpdate'] = self.datestr
        item['inserted']  = old_item['inserted']
        
        if 'price' in item:
            if 'price' in old_item and old_item['price'] != item['price']:
                item['priceHistory'][self.datestr] = item['price']
            first_price =  next(iter(item['priceHistory'].values())) 
            
            if "Původní cena" in item['items']:
                first_first = parse_int(item['items']["Původní cena"])
                if (not first_price) or first_first < first_price:
                    first_price = first_first
                    
                    first_date =  datetime.strptime(next(iter(item['priceHistory'].keys())), "%Y-%m-%d") - timedelta(days=1) 
                    dstr = first_date.strftime('%Y-%m-%d')
                    item["priceHistory"][ dstr] = first_price
            if "Zlevněno"  in item['items']:
                p = parse_int(item['items']["Zlevněno"])
                if p not in item['priceHistory'].values():
                    item['priceHistory'][self.datestr] = p
        
            if first_price:
                item['priceDropPercent'] = max(round ( (first_price - item['price'] ) / first_price , 3), 0)
                item['priceDropCzk'] = first_price - item['price']
        elif 'priceDropPercent' in old_item:
            item['priceDropPercent'] = old_item['priceDropPercent']  
            item['priceDropCzk'] = old_item['priceDropCzk'] 

        self.buffer.append(ReplaceOne({'_id': old_item['_id']}, item))

    def insert(self, item):
        self.insert_counter += 1

        item['priceHistory'] = {
            self.datestr: item.get('price', None)
        }
        item['inserted'] = self.datestr
        item['lastUpdate'] = self.datestr
        item['priceDropPercent'] = 0
        item['priceDropCzk'] = 0

        self.buffer.append(InsertOne(item))


    def flush_buffer(self, force=False):
        if len(self.buffer) >= self.batch_size or (force and len(self.buffer) > 0):
            
            self.collection.bulk_write(self.buffer)
            self.buffer = []
            self.buffer_size = 0
            self.spider.logger.info(f'Inserted {self.insert_counter} items, updated {self.update_counter} items')

    
