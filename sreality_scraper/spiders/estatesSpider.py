import scrapy
import json
from sreality_scraper.src.sreality import get_catalog_uris, deal_codes, property_codes, deal_codes_names, property_codes_names
import sreality_scraper.src.sreality as sreality
import sreality_scraper.src.utils as utils
from sreality_scraper.spiders.listingsCounterSpider import ListingsCounterSpider
from datetime import datetime

class EstatesSpider(ListingsCounterSpider):
    name = 'estates'


    custom_settings = {
        'ITEM_PIPELINES': {
            'sreality_scraper.pipelines.SaveToDbPipeline': 300,
        },
        'LOG_LEVEL': 'INFO',
        'LOG_FILE': f'logs/estates.log',	
    }

    include = { 
        'house': ['sell']
    }


    def handle(self, deal, prop, count):

        if prop not in self.include or deal not in self.include[prop]:
            
            self.logger.info(f"Skipping {prop} {deal}")
            return
        
        self.logger.info(f"Crawling {prop} {deal} {count}")
        urls = get_catalog_uris(deal, prop, count)

        for url in urls:
            yield scrapy.Request(url, callback=self.parse_estates)

    def parse_estates(self, response):
        jsonresponse = response.json() 

        for item in jsonresponse["_embedded"]['estates']:
            yield scrapy.Request( self.base_api_url + item['_links']['self']['href'] ,
                        callback=self.parse_detail_page)
            
    def parse_detail_page(self, response):  
        jsonresponse = response.json()        
        item = {} # empty item as distionary
        try:             
            item['prop'] = jsonresponse['seo']['category_main_cb']
            item['deal'] =  jsonresponse['seo']['category_type_cb']
            
            item['apiUrl'] = response.url
            item['id'] = response.url.split('/estates/')[1]
            item['meta'] = jsonresponse['meta_description']
            item['title'] = jsonresponse['name']['value']
            item['description'] = jsonresponse['text']['value']

            if jsonresponse['seo']:
                item['url'] = sreality.get_detail_url_from_seo_object(jsonresponse['seo'], item['id'])

            if jsonresponse['price_czk']:
                if jsonresponse['price_czk']['value']:
                    item['price'] =  jsonresponse['price_czk']['value'].replace(' ', '')
                if jsonresponse['price_czk']['unit']:
                    item['priceUnit'] =  jsonresponse['price_czk']['unit']
            else:
                item['price'] = ''

                
            item['longitude'] = jsonresponse['map']['lon']
            item['latitude'] = jsonresponse['map']['lat']

            item["address"] = jsonresponse['locality']['value']

            # gather images
            if  jsonresponse['_embedded']['images']:
                item['images'] = []
            
            for images in jsonresponse['_embedded']['images']:

                obj = {}                 
                # if images['_links']['dynamicDown']:
                # if images['_links']['gallery']:
                # if images['_links']['dynamicUp']:
                if images['_links']['self']:
                    obj['self'] = images['_links']['self']['href']
                if images['_links']['view']:
                    obj['view'] = images['_links']['view']['href']
                    
                item['images'].append(obj)


            # miscellenious items       
            if jsonresponse['items']:
                item['items'] = {}

                for i in jsonresponse['items']:
                    if  isinstance(i['value'] , list):
                        item['items'][i['name']]= ''
                        for j in i['value']:
                            item['items'][i['name']] += j['value'] + ', '
                        item['items'][i['name']] = item['items'][i['name']][:-2]   
                    else:
                        item['items'][i['name']] = i['value']
                    
        except Exception as e:
            self.logger.exception(f'Exception {e}. for url: {response.url}'  )
            
        yield item  
