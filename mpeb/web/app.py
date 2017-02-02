from flask import Flask
from flask_restless import APIManager
from flask_sqlalchemy import SQLAlchemy


def get_app(config):
    app = Flask(__name__)

    app.config.from_object('mpeb.web.config')
    app.config['SQLALCHEMY_DATABASE_URI'] = config.get_sqlalchemy_url()
    app.config['DEBUG'] = config.get_debug()
    db = SQLAlchemy(app)

    manager = APIManager(app, flask_sqlalchemy_db=db)

    
    class Config(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String)
    # Create API endpoints, which will be available at /api/<tablename> by
    # default. Allowed HTTP methods can be specified as well.
    manager.create_api(Config, methods=['GET', 'POST', 'DELETE'])

    db.create_all()

    return app





    
