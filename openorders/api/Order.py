from flask import Response, jsonify
from flask_restful import abort, Api, Resource
import json
from . import get_db


class Order(Resource):

    def get(self, order_id):
        with get_db() as cur:
            order_sql = """ SELECT json_agg(row_to_json(orders.*)) FROM

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
                        WHERE orders.id = %s
                        GROUP by orders.id, orders.order_count 
                        ) as orders;"""
            cur.execute(order_sql, ( str(order_id), ) )
            orders = cur.fetchone()

        if orders is None or orders[0] is None:
            pagination = {'offset': 0, 'current_count': 0,'total_count': 0 }
            res = { 'results': [], 'pagination':  pagination}
            return jsonify( **res )

        pagination = {'offset': 0, 'current_count': len(orders[0]),'total_count': len(orders[0]) }
        res = { 'results': orders[0], 'pagination': pagination   }         
        return jsonify( **res )