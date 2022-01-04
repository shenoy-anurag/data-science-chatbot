import asyncio
import copy
import logging
import os
from asyncio import AbstractEventLoop
from typing import Text, Optional

from sanic import response, Blueprint, Sanic
from sanic.response import HTTPResponse
from sanic.response import json as jsonify
from sanic_jwt import protected
from sanic_restful_api import Api, Resource

from app import app
from app.common.constants import (
    ROOT_FOLDER_PATH, URL_FORMAT, URL_FORMAT_SECURE, ENV_PRODUCTION
)
from app.utils import remove_null_values_from_dict
from rasa.core import agent
from rasa.core.agent import Agent
from rasa.core.utils import AvailableEndpoints, EndpointConfig

logger = logging.getLogger(__name__)

app_blueprint = Blueprint('app_blueprint')
api = Api(app_blueprint)

_endpoints = AvailableEndpoints.read_endpoints(os.path.join(ROOT_FOLDER_PATH, 'endpoints.yml'))

tracker_endpoint_config = {
    'store_type': 'mongod',
    'url': os.environ['MONGO_URI'],
    'db': os.environ['DB_NAME'],
    'collection': 'conversations',
    'username': os.environ.get('DB_USERNAME'),
    'password': os.environ.get('DB_PASSWORD'),
    'auth_source': os.environ['DB_NAME']
}
tracker_endpoint_config = remove_null_values_from_dict(tracker_endpoint_config)
_endpoints.tracker_store = EndpointConfig.from_dict(tracker_endpoint_config)

url_format = copy.deepcopy(URL_FORMAT_SECURE if os.environ['ENVIRONMENT'] == ENV_PRODUCTION else URL_FORMAT)
action_endpoint_config = {
    'url': url_format.format(host=os.environ['ACTIONS_HOST'], port=os.environ['ACTIONS_PORT']) + 'webhook'
}
_endpoints.action = EndpointConfig.from_dict(action_endpoint_config)

_action_endpoint = _endpoints.action

app.logger.debug(_endpoints.__dict__)


async def load_agent_on_start(
        model_path: Text,
        endpoints: AvailableEndpoints,
        remote_storage: Optional[Text],
        app: Sanic,
        loop: AbstractEventLoop,
) -> Agent:
    """Load an agent.
    Used to be scheduled on server start
    (hence the `app` and `loop` arguments).
    """
    app.agent = await agent.load_agent(
        model_path=model_path,
        remote_storage=remote_storage,
        endpoints=endpoints,
        loop=loop,
    )
    logger.info("Rasa server is up and running.")
    return app.agent


bot_agent = load_agent_on_start(
    model_path="/app/models/bot-v1.tar.gz",
    endpoints=_endpoints,
    remote_storage=None,
    app=app,
    loop=asyncio.get_event_loop()
)


async def handle_text_with_agent(agent, user_chat, sender_id):
    return await agent.handle_text(user_chat, sender_id=sender_id)


@app.get("/health")
async def health(_) -> HTTPResponse:
    """Ping endpoint to check if the server is running and well."""
    body = {"status": "ok"}
    return response.json(body, status=200)


@app.route("/protected")
@protected()
async def protected_api(request):
    print(request.json)
    print(request.token)
    return jsonify({"protected": True})


class Chat(Resource):
    @protected()
    async def post(self, request):
        user_text = request.json.get('chat')
        sender_id = request.json.get('id')
        return await agent.handle_text(user_text, sender_id=sender_id)


api.add_resource(Chat, '/chat', endpoint='chat')
