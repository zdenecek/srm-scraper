
from scrapy.crawler import CrawlerProcess
from scrapy import signals
from scrapy.signalmanager import dispatcher
from sreality_scraper.spiders.listingsCounterSpider import ListingsCounterSpider

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
