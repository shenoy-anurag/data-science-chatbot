from app import app

from app.master.views import app_blueprint

app.blueprint(app_blueprint)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
