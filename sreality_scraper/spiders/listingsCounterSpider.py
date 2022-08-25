import scrapy
import json
import sreality_scraper.model.sreality as sreality 

class ListingsCounterSpider(scrapy.Spider):
    name = 'count'

    per_page = 100
    base_api_url = 'https://www.sreality.cz/api'

    custom_settings = {
        'ITEM_PIPELINES': {
            # A
        }
    }

    def start_requests(self):

        for  deal_name, deal_key in sreality.deal_codes.items():
            for prop_name, prop_key in sreality.property_codes.items():
                yield scrapy.Request(self.base_api_url + f"/cs/v2/estates/count?category_main_cb={prop_key}&category_type_cb={deal_key}&locality_country_id=112", meta={ 'deal': deal_name, 'prop': prop_name })

    def parse(self, response):
        jsonresponse = response.json() 

        yield { response.meta["deal"] + ":" + response.meta["prop"] : jsonresponse['result_size']}
        
            
    
