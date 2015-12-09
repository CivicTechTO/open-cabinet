from scraper_duplicates import scrape_duplicateorder
import time


dup_ids = []

with open('duplicates.txt') as dup_file:
    dups = dup_file.read()
    dups = dups.split('\n')
    dup_ids.extend( dups )


for order_id in dup_ids:
    if order_id != '':
        target_id = order_id[:4] + order_id[-4:]
        print target_id
        try:
            scrape_duplicateorder( target_id )
        except Exception as e:
            with open('scrape.log', 'a') as scrapelog:
                err_str = "ALLDUPSRIPT " + str(target_id) + " : " + e.message + str( datetime.datetime.now() )
                scrapelog.write( err_str+u'\n' ) 