from flask import Flask
from flask_apscheduler import APScheduler
from .Database import db, Carpark
from datetime import datetime, timedelta
from logging.config import dictConfig
import os
import pytz

app = None

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
        'custom_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'default',
            'filename': os.getcwd() + '\myapp.log'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi', 'custom_handler']
    }
})

def create_app():
	global app
	app = Flask(__name__, instance_relative_config=False)
	app.config.from_object('Config.Config')
	app.app_context().push()
	db.init_app(app)
	scheduler = APScheduler()
	scheduler.init_app(app)
	start_time = datetime.now().replace(minute=0, second=0, microsecond=0)
	start_time += timedelta(hours=1)

	refresh_date = datetime.now()
	refresh_date = refresh_date.astimezone(pytz.timezone('Asia/Singapore'))\
	.replace(hour=1, minute=0, second=0, microsecond=0)
	day_of_week = refresh_date.weekday()
	if day_of_week != 0:#not sunday
		refresh_date -= timedelta(days = day_of_week)
	refresh_date = refresh_date.astimezone(pytz.UTC)

	with app.app_context():
		db.create_all()
		from . import DefaultRoutes
		from . import APIRoutes
		app.register_blueprint(APIRoutes.api_bp,url_prefix='/API')

	from .Job import HourlyDBUpdate, GrabWeeklyCarparklots
	scheduler.add_job(id='Hourly DB Update',func=HourlyDBUpdate, trigger='interval', hours=1, start_date=start_time)
	scheduler.add_job(id='Weekly History Update',func=GrabWeeklyCarparklots, trigger='interval', days=7, start_date=refresh_date)
	scheduler.start()

	return app
