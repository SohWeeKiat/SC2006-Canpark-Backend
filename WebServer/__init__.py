from flask import Flask
from flask_apscheduler import APScheduler
from .Database import db, Carpark

app = None

def create_app():
	global app
	app = Flask(__name__, instance_relative_config=False)
	app.config.from_object('Config.Config')
	app.app_context().push()
	db.init_app(app)
	scheduler = APScheduler()
	scheduler.init_app(app)
	scheduler.start()

	with app.app_context():
		db.create_all()
		from . import DefaultRoutes
	return app
