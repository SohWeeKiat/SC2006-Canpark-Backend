from datetime import datetime
from .Database.Carpark import Carpark
from .Database.CarparkLotRecordDate import CarparkLotRecordDate
from .Database.CarparkLotAvailability import CarparkLotAvailability
from .Database import db
from . import app
from .GovAPI import DataGov
from datetime import datetime, timedelta,timezone
import pytz

CarparkData = {}
CarparkHistory = {}

def GrabCarparkLotRecords(dt):
	record_date = CarparkLotRecordDate(dt.astimezone(pytz.UTC))
	record_date.Insert()
	data = DataGov.GetCarparkAvailability(dt.isoformat())
	for cp in data:
		if len(cp['carpark_info']) <= 0:
			continue
		info = cp['carpark_info'][0]
		cpa = CarparkLotAvailability(record_date.Id, cp['carpark_number'],
		info['total_lots'], info['lots_available'], info['lot_type'],
		datetime.fromisoformat(cp['update_datetime']).astimezone(pytz.UTC))
		cpa.Insert()

def InitializeDB():
	print("InitializeDB")
	with app.app_context():
		if Carpark.GetCount() <= 0:
			carparks = DataGov.GetCarparkList()
			for carpark in carparks:
				lat, long = DataGov.ConvertSVY21_WGS84(carpark['x_coord'], carpark['y_coord'])
				cp = Carpark(carpark['car_park_no'], carpark['address'],
					carpark['x_coord'], carpark['y_coord'],
					carpark['car_park_type'], carpark['type_of_parking_system'],
					carpark['short_term_parking'], carpark['free_parking'],
					carpark['night_parking'], carpark['car_park_decks'],
					carpark['gantry_height'], carpark['car_park_basement'],
					long, lat)
				cp.Insert()
			db.session.commit()
		if CarparkLotRecordDate.GetCount() <= 0:
			cur_date_time = datetime.now()
			cur_date_time = cur_date_time.replace(minute=0, second=0, microsecond=0)
			cur_date_time = cur_date_time.astimezone(pytz.timezone('Asia/Singapore'))
			for past_hr in range(0, 8 * 24):
				GrabCarparkLotRecords(cur_date_time)
				cur_date_time -= timedelta(hours=1)
			db.session.commit()
		GrabWeeklyCarparklots()
		#Carpark.GetCarparksTest()
	GrabLatestCarparklots()

def GrabLatestCarparklots():
	print("Updating carpark lots")
	data = DataGov.GetCarparkAvailability(datetime.now().astimezone(pytz.timezone('Asia/Singapore')).isoformat())
	for cp in data:
		if len(cp['carpark_info']) <= 0:
			continue
		info = cp['carpark_info'][0]
		cpa = CarparkLotAvailability(0, cp['carpark_number'],
		info['total_lots'], info['lots_available'], info['lot_type'],
		datetime.fromisoformat(cp['update_datetime']).astimezone(pytz.UTC))
		CarparkData[cp['carpark_number']] = cpa

def GrabWeeklyCarparklots():
	with app.app_context():
		all_carparks = Carpark.GetAllCarparks()
		for cp in all_carparks:
			history_hours, history_data = cp.GetPast7DaysSlots()
			CarparkHistory[cp.car_park_no] = {
				"start_date":history_hours[0][0],
				"end_date": history_hours[len(history_hours) - 1][0],
				"data":history_data
			}

def HourlyDBUpdate():
	print("HourlyDBUpdate")
	with app.app_context():
		cur_date_time = datetime.now()
		cur_date_time = cur_date_time.replace(minute=0, second=0, microsecond=0)
		cur_date_time = cur_date_time.astimezone(pytz.timezone('Asia/Singapore'))
		GrabCarparkLotRecords(cur_date_time)
		db.session.commit()
