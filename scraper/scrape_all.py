import datetime, argparse
from scraper import scrape_order
import time

limits = { 1990:2874, 1991:2595, 1992:2748, 1993:2223, 1994:2177, \
           1995:2258, 1996:2087, 1997:2058, 1998:2360, 1999:2287, \
           2000:1832, 2001:2426, 2002:2240, 2003:2158, 2004:1604, \
           2005:2342, 2006:1672, 2007:2027, 2008:1959, 2009:2071, \
           2010:1640, 2011:1728, 2012:1770, 2013:1510, 2014:1503, \
           2015:1219 }



def appendzeros(input_int):
    if len( str(input_int) ) == 4:
        return str(input_int)
    else:
        new_zeros = 4 - len( str(input_int) ) 
        zeros = ''.join(  [ '0' for elem in range(new_zeros) ] )
        return zeros + str(input_int)


def run_scrape(year=None, order_number=None):

    END_YEAR = 2016
    if year is None:
        START_YEAR = 1990
    else:
        START_YEAR = year

    if order_number is None:
        START_NUM = 1
    else:
        START_NUM = order_number

    for year in range( START_YEAR, END_YEAR ) :
        END_NUM = limits[year] + 1

        for ORDER_NUMBER in range( START_NUM, END_NUM ):

            ORDER_ID = str(year) + appendzeros( ORDER_NUMBER )
            print ORDER_ID

            try:
                scrape_order( ORDER_ID )

            except Exception as e:
                with open('scrape.log', 'a') as scrapelog:
                    err_str = str(year) + "-"+ str(ORDER_NUMBER) + " : " + e.message + str( datetime.datetime.now() )
                    scrapelog.write( err_str+u'\n' ) 

        START_NUM = 1
        



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scraper script to dl Orders DB.')
    parser.add_argument( '-o', dest='order_number', action="store", type=int,  help='order_number')
    parser.add_argument( '-y', dest='year', action="store", type=int,  help='year')

    args = parser.parse_args()
    print args.order_number
    print args.year

    if args.order_number is not None and len( str(args.order_number) ) > 4:
        print "invalid order_number length"
    elif args.year is not None and args.year not in xrange(1990, 2017):
        print "incorrect year component"
    else:
        run_scrape( args.year, args.order_number )