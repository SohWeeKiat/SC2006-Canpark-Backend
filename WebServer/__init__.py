from flask import Flask
from flask_apscheduler import APScheduler
from .Database import db, Carpark
from datetime import datetime, timedelta

app = None

def create_app():
	global app
	app = Flask(__name__, instance_relative_config=False)
	app.config.from_object('Config.Config')
	app.app_context().push()
	db.init_app(app)
	scheduler = APScheduler()
	scheduler.init_app(app)
	start_time = datetime.now().replace(minute=0, second=0)
	start_time += timedelta(hours=1)

	from .Job import HourlyDBUpdate
	scheduler.add_job(id='Hourly DB Update',func=HourlyDBUpdate, trigger='interval', hours=1, start_date=start_time)
	scheduler.start()

	with app.app_context():
		db.create_all()
		from . import DefaultRoutes
		from . import APIRoutes
		app.register_blueprint(APIRoutes.api_bp,url_prefix='/API')
	return app
