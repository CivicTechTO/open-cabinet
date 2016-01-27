## SETUP

1. Ensure you've got the Python dependencies in requirements.txt

2. Flesh out the CONFIG files. DBCONFIG.py in the /openorders folder and the /scraper. ALERTSCONFIG.py in the /openorders/alerts (has MailGun creds). FLASKCONFIG.py in /openorders. Remember to set DEBUG here to false in prod. 

3. Ensure your db is created w/ unicode encoding. Restore the db from the dump or... rescrape the site from scratch loool. (see README.md in /scraper)

4. Running python __init__.py (in /openorders) will get the Flask server running.

5. Search Page JS
   a) Install Node.
   b) Go into /openorders/static/js and run 'npm install' to get all the js dependencies.
   c) Running 'npm run dev' will get a webpack server to serve a bundle.js for dev purposes, ensure you're linking to the dev bundle.js at the bottom search.html file and escape the prod bundle.js and vice versa for dev purposes. (Alternatively branch dev & prod) Running 'webpack search.jsx bundle.js' will spit out a bundle.js for prod. 
All this is just for that search page's UI. If you can't find someone comfortable w/ React; get someone to do it in Angular or JQuery. Should be trivial.

6. Run a daily cron on dailyscrape.py. At the bottom I have an email sent for basic logging. Furbish your own Mailgun/mailer creds.

## TODO
1. The views in the alerts blueprint & associated Unsubscribe & confirmation page templates. (alerts/views.py)
2. Email Based
    * [ ] Confirmation email template 
	* [ ] Daily digest email template & associated dailymailer script. (+cron)
	* [ ] Alerts subscription page 
	* [ ] Decidce on email subscription service
3. A signup box on the homepage that posts to the subscribe view in alerts.
4. Categorization: keywords and alert filters
5. Vizualization: wordcloud from recent orders ?
6. Front-end TODO
   * [ ] page frameworks for alerts / search
   * [ ] js for options, popovers, boxes
   * [ ] js for search results
   * [ ] js + elastic search
7. Copy TODO
   * [ ] Contextual Help in alerts
