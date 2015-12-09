import datetime
from db import get_db
from scraper import scrape_order
from missing import spot_missing
import requests

###################################################
##     DAILY PROCESS
###################################################



def get_max_id_this_year():
    with get_db(True) as cur:
        cur.execute( """SELECT max(id) FROM orders
                        WHERE EXTRACT(YEAR FROM pub_date) = EXTRACT( YEAR FROM NOW() );""" )
        max_id = cur.fetchone()    
    if max_id is not None:
        max_id = max_id['max']
    return max_id



SCRAPE_RANGE = True
YEAR_INT = datetime.datetime.utcnow().year

old_max = get_max_id_this_year()

### NEW YEAR CASE - case where old_max is of last years
if old_max == None:
    # try to get 0001 for this year; 
    min_id = str(YEAR_INT) + "0001"
    scrape_order(min_id)
    new_max = get_max_id_this_year()
    if new_max == None:
        SCRAPE_RANGE = False
    else:
        old_max = new_max



if SCRAPE_RANGE == True:
    # get 9999 for year
    max_id = str(YEAR_INT) + "9999"
    scrape_order(max_id)
    new_max = get_max_id_this_year()
    target_list = range( old_max+1, new_max ) 
    # hit all in the middle
    for order_id in target_list:
        scrape_order(order_id)





###################################################
##     DAILY MISSING PROCESS
###################################################

with get_db(True) as cur:

    cur.execute("""SELECT max(id) FROM orders 
                    WHERE (add_time < current_timestamp - interval '2 hours') 
                        and ( EXTRACT(YEAR FROM pub_date) = EXTRACT( YEAR FROM NOW() ) );""" )
    b4today_id = cur.fetchone()

if b4today_id is not None:
    b4today_id = b4today_id['max']
missing_yesterday = []

if b4today_id != None:
    NEXT_YEAR = YEAR_INT + 1
    # uses spot_missing from missing.py
    missing_this_year = spot_missing( YEAR_INT, NEXT_YEAR  )
    missing_yesterday = [ elem for elem in missing_this_year if elem > b4today_id ]

###################################################
##     DAILY MAILER PROCESS
###################################################



with get_db(True) as cur:

    cur.execute(""" SELECT COUNT(*) as count FROM 
                    orders o
                    WHERE (o.add_time > current_timestamp - interval '2 hours')
                    ;""" )
    res = cur.fetchone()




count = res['count']
miss_count = len(missing_yesterday)


text = "Daily Log\n"
text = text + "Count: "+ str(count) + "\n"
text = text + "Missing: "+ str( miss_count) + "\n"
text = text + "Before Scrape: " + str( b4today_id ) + "\n"
text = text + "After Scrape: " + str( new_max ) + "\n" 


# FLESH w/ YOUR OWN CREDS
def send_simple_message(text):
    return requests.post(
        "MAILGUN POST ADDR",
        auth=("api", "YOUR API KEY"),
        data={"from": "ScraperLog <scraper@mailer.openorders.ca>",
              "to": ["nishav05@gmail.com"],
              "subject": "ScraperLog",
              "text": text})

# send_simple_message( text )