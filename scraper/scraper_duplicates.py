from bs4 import BeautifulSoup
import urllib2, datetime, time, re
import argparse
from db import get_db

ORDER_URL_START = "http://www.pco-bcp.gc.ca/oic-ddc.asp?lang=eng&Page=secretariats&txtOICID="
ORDER_URL_END = "&txtFromDate=&txtToDate=&txtPrecis=&txtDepartment=&txtAct=&txtChapterNo=&txtChapterYear=&txtBillNo=&rdoComingIntoForce=&DoSearch=Search+%2F+List"
ATTACHMENT_URL_STEM = "http://www.pco-bcp.gc.ca/"

EXTRA_PAGE_PARAM = "&pg="

regID_pattern = re.compile(r'[A-Z]{1,10}\/[0-9]{4}\-[0-9]{4}')
regDate_pattern = re.compile( r'[0-9]{4}-[0-9]{2}-[0-9]{2}')

#   PROCESS
#   scrape_order -> parse_tds -> insert_order 
#                                   -> scrape_attachment -> parse_attachment


def parse_attachment(id_str, dup_count, att_url, att_text):
    try:
        att_soup = BeautifulSoup( att_text, 'lxml' )
        ptags = att_soup.findAll('p')
        if re.match( 'Privy Council Office', ptags[0].text ):
            ptags = ptags[1:]

        ptags = [ tag.text.strip()  for tag in ptags ]
        att_str = " ".join( ptags )
        att_str = re.sub( u'\xa0', u' ', att_str )    # unicode for &nbsp;/HTML space -> ' '
        with get_db() as cur:
            cur.execute("""INSERT INTO 
                            attachments(order_id, attachment, url) 
                            SELECT %s, %s, %s
                            WHERE not exists 
                            ( SELECT 1 from attachments WHERE order_id=%s and url=%s);""", 
                        ( id_str, att_str,  att_url, id_str, att_url ) )
            cur.connection.commit()
    except Exception as e:
        with open('scrape.log', 'a') as scrapelog:
            err_str = id_str  + " att parse fail " + str(e) + " " +str( datetime.datetime.now() )
            scrapelog.write( err_str+u'\n' )   

def scrape_attachment(id_str, dup_count, link):
    att_url = ATTACHMENT_URL_STEM + link['href']

    try:
        r = urllib2.urlopen( att_url )
        if r.getcode() == 200:
            att_text = r.read()
            parse_attachment( id_str, dup_count, att_url, att_text )
        else:
            with open('scrape.log', 'a') as scrapelog:
                err_str = id_str  + "att link !200 " + str(e) + " " +str( datetime.datetime.now() )
                scrapelog.write( err_str+u'\n' )   


    except urllib2.HTTPError as e:
        with open('scrape.log', 'a') as scrapelog:
            err_str = id_str  + " att link fail " + str(e) + " " +str( datetime.datetime.now() )
            scrapelog.write( err_str+u'\n' )   


def insert_order(id_str, dup_count, subject, reg_id, reg_date, chapter, bill, precis, pub_date, url, links, acts, departments):
    with get_db() as cur:
        cur.execute("""INSERT INTO 
                        orders(id, order_count, subject, reg_id, reg_date, 
                              chapter, bill, precis, pub_date, url) 
                        SELECT %s, %s, %s, %s, %s, 
                               %s, %s, %s, %s, %s 
                        where not exists 
                            (select 1 from orders where id = %s and order_count = %s);""", 
                    ( id_str, dup_count, subject, reg_id, reg_date, 
                        chapter, bill, precis, pub_date, url, id_str, dup_count ) )
        cur.connection.commit()

    for link in links:
        scrape_attachment(id_str, dup_count, link)

    for act in acts:
        act_str = act.text.strip()
        act_str = re.sub( '\s\s+', u' ', act_str )
        with get_db() as cur:
            cur.execute("""INSERT INTO acts(order_id, order_count, act) 
                           SELECT %s, %s, %s
                           where not exists 
                            (select 1 from acts where order_id =%s and order_count = %s and act = %s);""", 
                        ( id_str, dup_count, act_str, id_str, dup_count, act_str ))            
            cur.connection.commit()
    
    for dept in departments:
        department = dept.text.strip()
        with get_db() as cur:
            cur.execute("""INSERT INTO departments(order_id, order_count, department) 
                            SELECT %s, %s, %s where not exists 
                            (select 1 from departments where order_id =%s and order_count = %s and department = %s);""", 
                        ( id_str, dup_count, department, id_str, dup_count, department ))
            cur.connection.commit()      

''' PARSE ORDER '''
def parse_tds(order_id, tds, dup_count=1):
    # NONE VARS
    curr_id = None
    pub_date, subject, reg_id, reg_date, chapter, bill, precis = None, None, None, None, None, None, None
    links, acts, departments = [], [], []

    for td in tds:

        if td['headers'][0] == u'number':

            # ENSURES YOU'VE LOOPED THROUGH FIRST ONE
            if (curr_id is not None):

                if ( str(order_id) == curr_id): 
                    insert_order(curr_id, dup_count, subject, reg_id, reg_date, chapter, bill, precis, pub_date, url, links, acts, departments)
                    time.sleep(0.1)
                    dup_count += 1
                    pub_date, subject, reg_id, reg_date, chapter, bill, precis = None, None, None, None, None, None, None
                    links, acts, departments = [], [], []

                else: 
                    return



            # FIRST LOOP ON SECOND+ PAGES FOR DUP CASE
            if (curr_id is None) and dup_count != 1:
                dup_count += 1


            url = ORDER_URL_START + str(order_id) + ORDER_URL_END
            if dup_count > 5:
                next_page = (dup_count/5) + 1
                url += EXTRA_PAGE_PARAM + str(next_page) 

            curr_id = td.text.split('-')[0]+td.text.split('-')[1]

        elif re.match('subject_', td['headers'][0] ):  
            subject = td.text.strip()  

        elif re.match('registrationtype', td['headers'][0] ):
            regID_matches = re.findall( regID_pattern, td.text )
            if len(regID_matches) == 1:
                reg_id = regID_matches[0].strip()
            regDate_matches = re.findall( regDate_pattern, td.text )
            if len(regDate_matches) == 1:
                reg_date = regDate_matches[0].strip()

        elif re.match('chapter', td['headers'][0]):
            chapter = td.text.strip()

        elif re.match('bill', td['headers'][0]):
            bill = td.text.strip()

        elif re.match('precis_', td['headers'][0]):
            precis = td.text.strip()

        elif re.match('date', td['headers'][0]):
            pub_date = td.text.strip()

        elif re.match( 'attachments',  td['headers'][0] ):
            links = td.findAll('a')

        elif re.match('act_', td['headers'][0]):
            acts = td.findAll('strong')

        elif re.match('departments', td['headers'][0]):
            departments = td.findAll('strong')

    # FOR FINAL DUP 
    if dup_count%5 == 0 and ( str(order_id) == curr_id):
        insert_order(curr_id, dup_count, subject, reg_id, reg_date, chapter, bill, precis, pub_date, url, links, acts, departments)
        time.sleep(0.1)

        next_page = (dup_count/5) + 1
        url = ORDER_URL_START + str(order_id) + ORDER_URL_END + EXTRA_PAGE_PARAM + str(next_page) 
        scrape_duplicateorder( order_id, url, dup_count )




''' ORDER_ID MUST HAVE YEAR AND ID SEPARATED BY - '''
def scrape_duplicateorder( order_id, order_url=None, dup_count=1 ):

        if order_url == None:
            order_url = ORDER_URL_START + str(order_id) + ORDER_URL_END

        r = urllib2.urlopen( order_url )

        if r.getcode() == 200:
            order_text = r.read()

            dirty_soup = BeautifulSoup( order_text, 'html.parser' )
            tds = dirty_soup.findAll('td', attrs={ 'headers': True } )

            if len(tds) != 0:
                parse_tds( order_id, tds, dup_count )
            else:
                with open('scrape.log', 'a') as scrapelog:
                    err_str = str(order_id)  + " NO-TDS "  +str( datetime.datetime.now() )
                    scrapelog.write( err_str+u'\n' )  

        else:
            with open('scrape.log', 'a') as scrapelog:
                err_str = str(order_id)  + " " +  str( r.getcode() ) + " "  +str( datetime.datetime.now() )
                scrapelog.write( err_str+u'\n' )  

        time.sleep(0.5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape and parse orders.')
    parser.add_argument( 'order_id', metavar='order_id', type=int, nargs=1, help='a valid order_id')
    args = parser.parse_args()
    target_id = args.order_id[0]

    if len( str(target_id) ) != 8:
        print "invalid order_id length"
    elif int(str(target_id)[0:4]) not in xrange(1990, 2017):
        print "incorrect year component"

    else:
        print target_id
        scrape_duplicateorder( target_id )