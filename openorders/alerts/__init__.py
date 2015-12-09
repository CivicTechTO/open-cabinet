from flask import Blueprint
from db import get_db

alerts_blueprint = Blueprint('alerts', __name__)

from . import views