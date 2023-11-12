from datetime import datetime
import scrapy
from sreality_scraper.src.smapy import get_reverse_geocode_url, parse_reverse_geocode_xml
import os
from pymongo import MongoClient


class LocalitySpider(scrapy.Spider):
    name = 'locality'
    collection_name = 'houses'

    custom_settings = {

        'LOG_LEVEL': 'INFO',
        'LOG_FILE': os.path.join(os.getenv("LOG_DIR"), f"locality-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.log"),
        'AUTOTHROTTLE_ENABLED':  True,
    }

    def start_requests(self):
        self.counter = 0
        self.client = MongoClient(
            self.settings.get("MONGODB_CONNECTION_STRING"))
        self.db = self.client[self.settings.get("MONGODB_DB")]
        self.coll = self.db[self.settings.get("MONGODB_COLLECTION")]

        query = {"deleted": {"$exists": False}, "location": {
            "$exists": True}, "locality": {"$exists": False}}

        for listing in self.coll.find(query):
            yield scrapy.Request(
                url=get_reverse_geocode_url(
                    *listing['location']['coordinates']),
                callback=self.handle,
                meta={'id': listing['_id']})

    def handle(self, response):

        locality = parse_reverse_geocode_xml(response.text)
        if locality:
            self.coll.update_one({ '_id': response.meta['id'] }, { '$set': { 'locality': locality } })
            self.counter += 1
            if self.counter % 100 == 0:
                self.logger.info(f'Updated {self.counter} items')

    def spider_closed(self, spider):
        self.client.close()
