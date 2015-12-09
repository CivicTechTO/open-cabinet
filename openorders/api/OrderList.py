from flask import jsonify, Response, request
from flask_restful import abort, Api, Resource, reqparse
from . import get_db
import urllib, datetime, json


class OrderList(Resource):

    def get(self):
        parser = reqparse.RequestParser(bundle_errors=True)

        def date_obj(date):
            return datetime.datetime.strptime(date, "%Y-%m-%d").date()

        parser.add_argument('keywords', type=str, help='Keywords?')
        parser.add_argument('actName', type=str, help='Act name')
        parser.add_argument('deptName', type=str, help='Dept name')
        parser.add_argument('billName', type=str, help='Bill name')
        parser.add_argument('startDate', type=date_obj, help='Start Date')
        parser.add_argument('endDate', type=date_obj, help='End Date')
        parser.add_argument('parseDate', type=date_obj, help='Parse Date')
        parser.add_argument('offset', type=int, help='Offset')


        args = parser.parse_args()

        keywords = '{}'
        if args['keywords'] is not None:
            keywords = urllib.unquote(args['keywords'])
            keywords = keywords.split(" ")
            keywords = [ '%'+keyword+'%' for keyword in keywords ]


        actName = None
        if args['actName'] is not None:
            actName = urllib.unquote( args['actName'] )
        deptName = None
        if args['deptName'] is not None:
            deptName = urllib.unquote( args['deptName'] )
        billName = None
        if args['billName'] is not None:
            billName = urllib.unquote( args['billName'] )

        limit = 50
        offset = 0
        if args['offset'] is not None:
            offset = args['offset']




        with get_db() as cur:

            count_sql = """ SELECT COUNT(*) FROM
                        (SELECT orders.*
                        FROM 
                        orders 
                        left join acts on acts.order_id = orders.id and acts.order_count = orders.order_count
                        left join departments on departments.order_id = orders.id and departments.order_count = orders.order_count
                        left join attachments on attachments.order_id = orders.id and attachments.order_count = orders.order_count
                        WHERE (%s IS NULL or acts.act = %s)
                        and (%s IS NULL or departments.department = %s)
                        and (%s IS NULL or orders.bill = %s)
                        and ( (%s IS NULL or %s IS NULL) or ( orders.pub_date >= %s and orders.pub_date <= %s ) )
                        and ( %s = '{}' or precis ILIKE ALL( %s )  )
                        and ( %s is NULL or  orders.add_time::DATE  = %s )
                        GROUP by orders.id, orders.order_count 
                        ORDER by orders.id DESC, orders.order_count DESC
                        ) as orders;"""

            cur.execute( count_sql, ( actName, actName, 
                                    deptName, deptName, 
                                    args['billName'], args['billName'], 
                                    args['startDate'], args['endDate'], args['startDate'], args['endDate'],
                                    keywords, keywords,
                                    args['parseDate'], args['parseDate'], ) )
            count = cur.fetchone()
            totalcount = count[0]

            orders_sql = """ SELECT json_agg(row_to_json(orders.*)) as orders FROM
                        (SELECT orders.bill, orders.chapter, orders.bill, orders.order_count,
                                orders.id, orders.precis, orders.subject, orders.pub_date,
                                orders.reg_id, orders.reg_date, orders.url, 
                        case when count(acts) = 0 then '[]' else json_agg(distinct acts.act) end as acts,
                        case when count(departments) = 0 then '[]' else json_agg(distinct departments.department) end as departments,
                        case when count(attachments) = 0 then '[]' else json_agg(distinct attachments.attachment) end as attachments,
                        case when count(attachments) = 0 then '[]' else json_agg(distinct attachments.url) end as attachment_urls
                        FROM 
                        orders 
                        left join acts on acts.order_id = orders.id and acts.order_count = orders.order_count
                        left join departments on departments.order_id = orders.id and departments.order_count = orders.order_count
                        left join attachments on attachments.order_id = orders.id and attachments.order_count = orders.order_count
                        left join acts act2 on act2.order_id = orders.id and act2.order_count = orders.order_count
                        left join departments dept2 on dept2.order_id = orders.id and dept2.order_count = orders.order_count
                        WHERE (%s IS NULL or act2.act = %s)
                        and (%s IS NULL or dept2.department = %s)
                        and (%s IS NULL or orders.bill = %s)
                        and ( (%s IS NULL or %s IS NULL) or ( orders.pub_date >= %s and orders.pub_date <= %s ) )
                        and ( %s = '{}' or precis ILIKE ALL( %s )  )
                        and ( %s is NULL or  orders.add_time::DATE  = %s )
                        GROUP by orders.id, orders.order_count 
                        ORDER by orders.id DESC, orders.order_count DESC LIMIT 50 OFFSET %s
                        ) as orders;"""
            cur.execute(orders_sql, ( actName, actName, 
                                    deptName, deptName, 
                                    args['billName'], args['billName'], 
                                    args['startDate'], args['endDate'], args['startDate'], args['endDate'],
                                    keywords, keywords,
                                    args['parseDate'], args['parseDate'], 
                                    offset, ) )
            orders = cur.fetchone()


        if orders is None or orders[0] is None:
            pagination = {'offset': 0, 'current_count': 0,'total_count': 0, 'limit': 50}
            res = { 'results': [], 'pagination': pagination  }
            return jsonify( **res )   

        pagination = { 'limit':50, 'offset': offset, 'current_count': len( orders[0]) ,'total_count': totalcount }
        res = { 'pagination': pagination, 'results': orders[0]  }              
        return jsonify( **res )