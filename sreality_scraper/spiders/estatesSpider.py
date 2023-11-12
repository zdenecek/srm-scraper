from datetime import datetime
import scrapy
from scrapy.exceptions import DropItem
from sreality_scraper.src.sreality import get_catalog_uris
import sreality_scraper.src.sreality as sreality
import sreality_scraper.src.utils as utils
from sreality_scraper.spiders.listingsCounterSpider import ListingsCounterSpider
import os


class EstatesSpider(ListingsCounterSpider):
    name = 'estates'

    custom_settings = {
        'ITEM_PIPELINES': {
            'sreality_scraper.pipelines.SaveToDbPipeline': 300,
        },
        'LOG_LEVEL': 'INFO',
        'LOG_FILE': os.path.join(os.getenv("LOG_DIR"), f"estates-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.log"),
    }

    include = {
        'house': ['sell', 'rent', 'auction', 'shares'],
        'apartment': ['sell', 'rent', 'auction', 'shares'],
        'commercial': ['sell', 'rent', 'auction', 'shares'],
        'parcel': ['sell', 'rent', 'auction', 'shares'],
        'other': ['sell', 'rent', 'auction', 'shares'],
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.callback = self.handle

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
            yield scrapy.Request(self.base_api_url + item['_links']['self']['href'],
                                 callback=self.parse_detail_page)

    def parse_detail_page(self, response):
        jsonresponse = response.json()
        item = {}
        try:
            self.scrape_meta_data(response, jsonresponse, item)
            self.scrape_price_data(jsonresponse, item)
            self.scrape_locality_data(jsonresponse, item)
            self.scrape_image_data(jsonresponse, item)
            self.scrape_items_data(jsonresponse, item)

        except DropItem:
            return None
        except Exception as e:
            self.logger.exception(f'Exception {e}. for url: {response.url}')

        yield item

    def scrape_meta_data(self, response, jsonresponse, item):
        item['prop'] = jsonresponse['seo']['category_main_cb']
        item['deal'] = jsonresponse['seo']['category_type_cb']
        if 'category_sub_cb' in jsonresponse['seo']:
            item['sub'] = jsonresponse['seo']['category_sub_cb']

        if 'ownership' in jsonresponse['codeItems']:
            item['ownership'] = jsonresponse['codeItems']['ownership']

        item['apiUrl'] = response.url
        item['id'] = response.url.split('/estates/')[1]
        item['meta'] = jsonresponse['meta_description']
        item['title'] = jsonresponse['name']['value']
        item['description'] = jsonresponse['text']['value']

        if jsonresponse['seo']:
            item['url'] = sreality.get_detail_url_from_seo_object(
                jsonresponse['seo'], item['id'])

    def scrape_price_data(self, jsonresponse, item):
        if 'price_czk' in jsonresponse:
            if 'value_raw' in jsonresponse['price_czk']:
                item['price'] = jsonresponse['price_czk']['value_raw']
            if 'value' in jsonresponse['price_czk'] and jsonresponse['price_czk']['value'] != '':
                item['price'] = utils.parse_int(jsonresponse['price_czk']['value'])
            if 'unit' in jsonresponse['price_czk']:
                item['priceUnit'] = jsonresponse['price_czk']['unit']
                
        


    def scrape_locality_data(self, jsonresponse, item):

        if 'locality' in jsonresponse and 'value' in jsonresponse['locality']:
            item['address'] = jsonresponse['locality']['value']

        if 'map' in jsonresponse:
            source = jsonresponse['map']
        else:
            source = utils.get_closest_poi(jsonresponse)
        
        if source and (-180 < source['lon'] < 180 and -90 <  source['lat'] < 90):
            item['location'] = {
                    "type": "Point",
                    "coordinates": [source['lon'], source['lat']]
                }
        else:
            raise DropItem()


    def scrape_image_data(self, jsonresponse, item):
        if 'images' in jsonresponse['_embedded']:
            item['images'] = []

            for images in jsonresponse['_embedded']['images']:
                obj = {}
                if 'self' in images['_links']:
                    obj['self'] = images['_links']['self']['href']
                if 'view' in images['_links']:
                    obj['view'] = images['_links']['view']['href']
                if 'gallery' in images['_links']:
                    obj['gallery'] = images['_links']['gallery']['href']

                item['images'].append(obj)

    def scrape_items_data(self, jsonresponse, item):
        if jsonresponse['items']:
            item['items'] = {}

            for i in jsonresponse['items']:
                if i['name'] == "Cena za m²":
                    item['pricePerMeter'] = utils.parse_int(i['value'])
                elif i['name'] == "Užitná plocha":
                    item['usableArea'] = utils.parse_int(i['value'])
                elif i['name'] == "Plocha pozemku":
                    item['landArea'] = utils.parse_int(i['value'])
                elif isinstance(i['value'], list):
                    item['items'][i['name']] = ''
                    for j in i['value']:
                        item['items'][i['name']] += j['value'] + ', '
                    item['items'][i['name']] = item['items'][i['name']][:-2]
                else:
                    item['items'][i['name']] = i['value']
