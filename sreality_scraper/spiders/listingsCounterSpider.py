import scrapy
import json
import logging
import sreality_scraper.src.sreality as sreality 

class ListingsCounterSpider(scrapy.Spider):
    name = 'count'

    per_page = 100
    base_api_url = 'https://www.sreality.cz/api'
    

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)
        logger = logging.getLogger('scrapy.spidermiddlewares.httperror')
        logger.setLevel(logging.WARNING)
        logger = logging.getLogger('scrapy.core.scraper')
        logger.setLevel(logging.WARNING)
        logger = logging.getLogger('scrapy.core.engine')
        logger.setLevel(logging.WARNING)
        self.callback = self.handle_print
        self.sum = 0

    def start_requests(self):
        for  deal_name, deal_key in sreality.deal_codes.items():
            for prop_name, prop_key in sreality.property_codes.items():
                yield scrapy.Request(self.base_api_url + f"/cs/v2/estates/count?category_main_cb={prop_key}&category_type_cb={deal_key}&locality_country_id=112", meta={ 'deal': deal_name, 'prop': prop_name })
   
    def parse(self, response):
        jsonresponse = response.json() 
        deal, prop, count = response.meta["deal"],  response.meta["prop"], jsonresponse['result_size']
        self.sum += count    

        yield from self.callback( deal, prop, count) 

            
    def handle_print(self, deal, prop, count): 
        self.logger.info( f"{deal}:{prop} { count}")
        yield { deal: deal, prop: prop, count: count }
    
    def closed(self, reason):
        self.logger.info( f"Total: {self.sum}")
        
            
    
