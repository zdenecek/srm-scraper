import scrapy
import json
from sreality_scraper.model.sreality import get_catalog_uris, deal_codes, property_codes, deal_codes_names, property_codes_names


class EstatesSpider(scrapy.Spider):
    name = 'estates'

    #max_pages = 2
    base_api_url = 'https://www.sreality.cz/api'
    
    start_urls = get_catalog_uris(deal_codes["sell"], property_codes["house"], 1) 


    custom_settings = {
        'ITEM_PIPELINES': {
            'sreality_scraper.pipelines.SaveToDbPipeline': 300,
        }
    }


    def parse(self, response):
        jsonresponse = response.json() 

        for item in jsonresponse["_embedded"]['estates']:
            yield scrapy.Request( self.base_api_url + item['_links']['self']['href'] ,
                        callback=self.parse_detail_page)
            
    def parse_detail_page(self, response):  
        jsonresponse = response.json()        
        item = {} # empty item as distionary
        try:             
            # check if the property is an apartment (1) or a house (2)
            if jsonresponse['seo']['category_main_cb'] and 1 <= jsonresponse['seo']['category_main_cb'] <= 2:                
                item['PROPERTY_CODE'] = property_codes_names[ jsonresponse['seo']['category_main_cb'] ]
                item['DEAL_CODE'] = deal_codes_names[ jsonresponse['seo']['category_type_cb'] ]
                # house     -  category_main_cb=2
                # apartment - category_main_cb=1
                # pronájmu - rent     category_type_cb=2
                # prodej   - sell     category_type_cb=1
            else:
                return       

            item['API_URL'] = response.url
            item['ID'] = response.url.split('/estates/')[1]
            item['meta'] = jsonresponse['meta_description']
            item['TITLE'] = jsonresponse['name']['value']
            item['DESCRIPTION'] = jsonresponse['text']['value']
            
            if jsonresponse['price_czk']['value']:
                item['PRICE'] =  jsonresponse['price_czk']['value']
            else:
                item['PRICE'] = ''
            item['LONGITUDE'] = jsonresponse['map']['lon']
            item['LATITUDE'] = jsonresponse['map']['lat']

            item["ADDRESS"] = jsonresponse['locality']['value']

            # gather images
            item['IMAGES'] = []
            
            for images in jsonresponse['_embedded']['images']:                 
                if images['_links']['dynamicDown']:
                    item['IMAGES'].append( images['_links']['dynamicDown']['href'])
                if images['_links']['gallery']:
                    item['IMAGES'].append(images['_links']['gallery']['href'])
                if images['_links']['self']:
                    item['IMAGES'].append(images['_links']['self']['href'])
                if images['_links']['dynamicUp']:
                    item['IMAGES'].append(images['_links']['dynamicUp']['href'])
                if images['_links']['view']:
                    item['IMAGES'].append(images['_links']['view']['href'])

            # miscellenious items       
            for i in jsonresponse['items']:
                if isinstance(i['value'] , list):
                    item[i['name']]= ''
                    for j in i['value']:
                        item[i['name']] += j['value'] + ', '
                    item[i['name']] = item[i['name']][:-2]   
                else:
                    item[i['name']] = i['value']
                    
        except Exception as e:
            print ('Error: ' , e, '. for url: ',   response.url  )
            
        yield item  
