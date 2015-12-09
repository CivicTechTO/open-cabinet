from flask import Blueprint
from flask_restful import Api
from db import get_db

api_blueprint = Blueprint('api', __name__)

api = Api(api_blueprint)

from Order import Order
from OrderList import OrderList

api.add_resource(OrderList, 'orders')
api.add_resource(Order, 'orders/<int:order_id>')