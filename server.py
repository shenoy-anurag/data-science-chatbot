from app import bot_app

from app.master.views import app_blueprint

bot_app.blueprint(app_blueprint)

if __name__ == "__main__":
    bot_app.run(host="0.0.0.0", port=5000, debug=True)
