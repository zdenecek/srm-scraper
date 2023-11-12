
from scrapy.crawler import CrawlerProcess
from scrapy import signals
from scrapy.signalmanager import dispatcher
from sreality_scraper.spiders.listingsCounterSpider import ListingsCounterSpider
from sreality_scraper.src.sreality import property_codes

def get_listings_counts():
    process = CrawlerProcess()

    results = {}

    def crawler_results(signal, sender, item, response, spider):
        key = next(iter(item))
        type, cat = key.split(':')
        if cat not in results:
            results[cat] = {}
        results[cat][type] = item[key]

    
    dispatcher.connect(crawler_results, signal=signals.item_passed)

    process.crawl(ListingsCounterSpider)
    process.start()
    return results

def get_area_from_metadata(item):
    return None, None

def get_area_from_listing(item): 
    if item['prop'] == property_codes['parcel'] :
        if  'landArea' in item:
            return  item['landArea'], 'landArea'
        elif 'items' in item and "Plocha pozemku" in item['items']:
            return  int(item['items']["Plocha pozemku"]), 'landArea'

    elif item['prop'] in [property_codes['house'], property_codes['apartment']] :
        if 'usableArea' in item:
            return item['usableArea'], 'usableArea'
        if 'items' in item and 'Užitná plocha' in item['items']: 
            return int(item['items']['Užitná plocha']), 'usableArea'
    else:
        return get_area_from_metadata(item)


def get_closest_poi(item):

    source = None
    fields = ['poi_doctors', 'poi_leisure_time', 'poi_school_kindergarten', 'poi_transport', 'poi_grocery', 'poi_restaurant']
    for field in fields:
        if field in item and 'values' in item[field]:
            if source == None or source['distance'] > item[field]['values'][0]['distance']:
                source = item[field]['values'][0]


    return source

def parse_int(string):
    return int(''.join(filter(str.isdigit, string)))