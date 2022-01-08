import datetime
import logging
import os

from pymongo import MongoClient
from sanic import Sanic
from sanic_cors import CORS
from sanic_jwt import Initialize

from app.utils import authenticate

logger = logging.getLogger(__name__)

bot_app = Sanic(__name__)

CORS(bot_app)

Initialize(bot_app, authenticate=authenticate)

JWT_ACCESS_TOKEN_TIMEDELTA = datetime.timedelta(minutes=20)
JWT_REFRESH_TOKEN_TIMEDELTA = datetime.timedelta(hours=6)

security_settings = {
    'JWT_SECRET_KEY': 'my-local-secret',
    'JWT_ACCESS_TOKEN_EXPIRES': 900,
    'JWT_REFRESH_TOKEN_EXPIRES': 86400,
    'JWT_USERNAME': 'user',
    'JWT_PASSWORD': 'password'
}

bot_app.config.update(security_settings)

# app.config['CUSTOM_VALUE'] = 10

mongo_client = MongoClient(os.environ['MONGO_URI'])
db_name = mongo_client.get_database(os.environ['DB_NAME'])
