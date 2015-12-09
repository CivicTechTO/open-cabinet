###SCRAPER 
(If you wanna rescrape instead of just reload the db dump)

1. Create a db (w/ UTF8 Encoding). Furbish DBCONFIG creds. Create the tables etc using init_db.py

2. Run scraper_all to get rescrape the Orders site. Ensure the db creds are provided in DBCONFIG.py. The scrape.log will show you where it goes off. Ignore the dups. You can start it from any specific order by calling scrape_all -y YYYY -o ### . You can run/troubleshoot any specific order by running the scraper with scraper.py YYYY####. The totals will generally line up with the totals in the limits dict used in scrape_all.py. Any differences will generally be caught in the scrape.log and can be rerun individually w/ scraper.py.

3. Unfortunately the original scraper and the daily scrape process was designed with the assumption that order ids are unique and that only the very first order for each target page was required. Turns out order ids aren't unique. Luckily this is a legacy issue (1990-1997). I hacked together another version of the original scraper to deal with the doubles. Run scrape_alldups.py to get the doubles. It works off the file duplicates.txt. The original scraper.py now looks for and logs duplicates if they are seen in the future but won't actually scrape the doubles. Theres 1139 of them in total.

4. Run missing.py to populate the missing table with all the missing orders. There should be 44 up to 20151070.