from src.routes.routes import flask_application


if __name__ == "__main__":
    flask_application.run('0.0.0.0', 5000)
