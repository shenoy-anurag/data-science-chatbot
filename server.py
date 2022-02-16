import os

from app import bot_app

from app.master.views import app_blueprint

bot_app.blueprint(app_blueprint)

if __name__ == "__main__":
    bot_app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 8000)),
        workers=int(os.environ.get('WEB_CONCURRENCY', 1)),
        debug=bool(os.environ.get('DEBUG', ''))
    )
