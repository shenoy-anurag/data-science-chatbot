import os
import logging
from functools import wraps

from sanic.response import json as jsonify
from sanic import response
from sanic_jwt import exceptions

logger = logging.getLogger(__name__)


async def authenticate(request, *args, **kwargs):
    if not request.json:
        # return jsonify({'status': API_STATUS_FAILURE, "msg": "Missing JSON in request"})
        raise exceptions.AuthenticationFailed("Missing username or password.")

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not username or not password:
        # return jsonify({'status': API_STATUS_FAILURE, "msg": "Missing username parameter"})
        raise exceptions.AuthenticationFailed("Missing username or password.")

    if username != os.environ['JWT_USERNAME'] or password != os.environ['JWT_PASSWORD']:
        # return jsonify({'status': API_STATUS_FAILURE, "msg": "Bad username or password"})
        raise exceptions.AuthenticationFailed()

    return {'user_id': username}


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        request = args[0]
        token = request.json.get('token', '')
        logger.debug("user token")
        logger.debug(token)
        try:
            db_token = '12345'
            logger.debug("this is db token")
            logger.debug(db_token)
            if token != db_token:
                return response.text('Token is missing or invalid!')
        except:
            return response.text('Token is missing or invalid!')
        return f(*args, **kwargs)

    return decorated


def remove_null_values_from_dict(dic: dict, aggressive=False):
    null_keys = []
    for key, value in dic.items():
        if value is None:
            null_keys.append(key)
        if aggressive and not value:
            null_keys.append(key)
    for key in null_keys:
        dic.pop(key)
    return dic
