from flask import Flask, jsonify, Response, request, render_template
from jinja2 import Environment, FileSystemLoader

from db import get_db
from api import api_blueprint
from alerts import alerts_blueprint

# Used to construct url from missing order_ids in jinja template
ORDER_URL_START = "http://www.pco-bcp.gc.ca/oic-ddc.asp?lang=eng&Page=secretariats&txtOICID="
ORDER_URL_END = "&txtFromDate=&txtToDate=&txtPrecis=&txtDepartment=&txtAct=&txtChapterNo=&txtChapterYear=&txtBillNo=&rdoComingIntoForce=&DoSearch=Search+%2F+List"


app = Flask(__name__, static_url_path='/static')
app.config.from_object('FLASKCONFIG')


env = Environment(loader=FileSystemLoader('templates/'))

app.register_blueprint(api_blueprint, url_prefix='/api/')
app.register_blueprint(alerts_blueprint, url_prefix='/alerts/')


@app.route("/#api", methods=['GET'])
@app.route("/#data", methods=['GET'])
@app.route("/#secret", methods=['GET'])
@app.route("/", methods=['GET'])
def index():
    with get_db(True) as cur:
        cur.execute(""" SELECT orders.*, 
                        case when count(acts) = 0 then '[]' else json_agg(distinct acts.act) end as acts,
                        case when count(departments) = 0 then '[]' else json_agg(distinct departments.department) end as departments,
                        case when count(attachments) = 0 then '[]' else json_agg(distinct attachments.attachment) end as attachments,
                        case when count(attachments) = 0 then '[]' else json_agg(distinct attachments.url) end as attachment_urls
                        FROM 
                        orders 
                        left join acts on acts.order_id = orders.id and acts.order_count = orders.order_count
                        left join departments on departments.order_id = orders.id and departments.order_count = orders.order_count
                        left join attachments on attachments.order_id = orders.id and attachments.order_count = orders.order_count
                        GROUP by orders.id, orders.order_count 
                        ORDER by orders.pub_date DESC, orders.id DESC, orders.order_count DESC LIMIT 10""")
        recent_orders = cur.fetchall()

        cur.execute("""SELECT years.* FROM
                        (
                        SELECT ARRAY_AGG(order_id) as orders, SUBSTR(order_id::VARCHAR, 1, 4) as year
                        FROM missing
                        WHERE SUBSTR(order_id::VARCHAR, 1, 4)::INT > 2000
                        GROUP by year
                        ORDER BY year DESC
                        ) as years;""")
        missing_orders = cur.fetchall()


    return render_template('index.html', recent_orders=recent_orders, missing_orders=missing_orders,\
                             ORDER_URL_START=ORDER_URL_START, ORDER_URL_END=ORDER_URL_END)


@app.route("/search", methods=['GET'])
def search():
    return render_template('search.html')




if __name__ == "__main__":
    app.run()
