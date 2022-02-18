import asyncio
import copy
import logging
import os
import traceback
from asyncio import AbstractEventLoop
from typing import Text, Optional

from sanic import response, Blueprint, Sanic
from sanic.response import json as jsonify
from sanic_jwt import protected
from sanic_restful_api import Api, Resource

from app import bot_app
from app.common.constants import (
    URL_FORMAT, URL_FORMAT_SECURE, ENV_PRODUCTION, ENV_DEVELOPMENT, DOMAIN_FILE, CONFIG_FILE,
    ENDPOINTS_FILE, NLU_MAIN_FILE, NLU_RULES_FILE, NLU_STORIES_FILE
)
from app.utils import remove_null_values_from_dict
from rasa.core import agent
from rasa.core.agent import Agent
from rasa.core.utils import AvailableEndpoints, EndpointConfig
from rasa.model_training import train

logger = logging.getLogger(__name__)

app_blueprint = Blueprint('app_blueprint')
api = Api(app_blueprint)

loop = asyncio.get_event_loop()

_endpoints = AvailableEndpoints.read_endpoints(ENDPOINTS_FILE)

try:
    tracker_endpoint_config = {
        'store_type': 'mongod',
        'url': os.environ['MONGO_URI'],
        'db': os.environ['DB_NAME'],
        'collection': 'conversations',
        'username': os.environ.get('DB_USERNAME'),
        'password': os.environ.get('DB_PASSWORD'),
        'auth_source': os.environ.get('DB_AUTH', 'admin')
    }
    tracker_endpoint_config = remove_null_values_from_dict(tracker_endpoint_config)
    _endpoints.tracker_store = EndpointConfig.from_dict(tracker_endpoint_config)
except:
    # use in-memory tracker
    pass

url_format = copy.deepcopy(
    URL_FORMAT_SECURE if os.environ.get('ENVIRONMENT', ENV_DEVELOPMENT) == ENV_PRODUCTION else URL_FORMAT)
action_endpoint_config = {
    'url': url_format.format(
        host=os.environ.get('ACTIONS_HOST', "localhost"),
        port=":" + os.environ.get('ACTIONS_PORT', "5055") if os.environ.get('ACTIONS_PORT') else "") + 'webhook'
}
_endpoints.action = EndpointConfig.from_dict(action_endpoint_config)

_action_endpoint = _endpoints.action

logger.debug(_endpoints.__dict__)

BOT_AGENT = agent.Agent()


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
    global BOT_AGENT
    bot_agent = await agent.load_agent(
        model_path=model_path,
        remote_storage=remote_storage,
        endpoints=endpoints,
        loop=loop,
    )
    BOT_AGENT = bot_agent
    logger.info("Rasa server is up and running.")
    return BOT_AGENT


if os.path.exists("./models/20220217-182725-warm-quarter.tar.gz"):
    # model_path="./models/bot-v1.tar.gz"
    bot_agent = loop.run_until_complete(
        load_agent_on_start(
            model_path="./models/20220217-182725-warm-quarter.tar.gz",
            endpoints=_endpoints,
            remote_storage=None,
            app=bot_app,
            loop=asyncio.get_event_loop()
        )
    )


async def handle_text_with_agent(agent, user_chat, sender_id):
    return await agent.handle_text(user_chat, sender_id=sender_id)


class Health(Resource):
    async def get(self):
        body = {"status": "ok"}
        return response.json(body, status=200)


class Protected(Resource):
    @protected()
    async def protected_api(self, request):
        print(request.json)
        print(request.token)
        return jsonify({"protected": True})


class LoadAgent(Resource):
    @protected()
    async def post(self, request):
        global BOT_AGENT
        try:
            if os.path.exists("./models/20220217-182725-warm-quarter.tar.gz"):
                # model_path="./models/bot-v1.tar.gz"
                await load_agent_on_start(
                    model_path="./models/20220217-182725-warm-quarter.tar.gz",
                    endpoints=_endpoints,
                    remote_storage=None,
                    app=bot_app,
                    loop=asyncio.get_event_loop()
                )
            return jsonify({'status': 200, 'message': 'success', 'data': "loading"})
        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())
            return jsonify({'status': 500, 'message': 'error', 'error': str(e)}, status=500)


class TrainBot(Resource):
    @protected()
    async def post(self, request):
        nlu_files = [NLU_MAIN_FILE, NLU_RULES_FILE, NLU_STORIES_FILE]
        try:
            training_result = train(domain=DOMAIN_FILE, config=CONFIG_FILE, training_files=nlu_files)
            output_path = training_result.model
            bot_agent = load_agent_on_start(
                model_path=output_path,
                endpoints=_endpoints,
                remote_storage=None,
                app=bot_app,
                loop=asyncio.get_event_loop()
            )
            return jsonify({'status': 200, 'message': 'success', 'data': "training"})
        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())
            return jsonify({'status': 500, 'message': 'error', 'error': str(e)}, status=500)


class Chat(Resource):
    @protected()
    async def post(self, request):
        try:
            user_text = request.json.get('chat')
            sender_id = request.json.get('id')
            return await BOT_AGENT.handle_text(user_text, sender_id=sender_id)
        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())
            return jsonify({'status': 500, 'message': 'error', 'error': str(e)}, status=500)


api.add_resource(Health, '/')
api.add_resource(Protected, '/protected', endpoint='protected')
api.add_resource(Chat, '/chat', endpoint='chat')
api.add_resource(TrainBot, '/train', endpoint='train')
api.add_resource(LoadAgent, '/load-model', endpoint='load-model')
