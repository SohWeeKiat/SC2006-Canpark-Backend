from datetime import datetime
from .Database.Carpark import Carpark
from .Database.CarparkLotRecordDate import CarparkLotRecordDate
from .Database.CarparkLotAvailability import CarparkLotAvailability
from .Database import db
from . import app
from .GovAPI import DataGov
from datetime import datetime, timedelta,timezone
import pytz
import logging

CarparkData = {}
CarparkHistory = {}
CarparkView = {}
CarparkAvgMovement = {}

def InsertCarparkView(car_park_no, UUID):
	if car_park_no not in CarparkView.keys():
		CarparkView[car_park_no] = []
		CarparkView[car_park_no].append({
			"UUID" : UUID,
			"last_view_time": datetime.now()
		})
	else:
		found = False
		count = len(CarparkView[car_park_no])
		for index in range(0, count):
			if CarparkView[car_park_no][index]["UUID"] == UUID:
				found = True
				CarparkView[car_park_no][index] = {
					"UUID" : UUID,
					"last_view_time": datetime.now()
				}
				break
		if not found:
			CarparkView[car_park_no].append({
				"UUID" : UUID,
				"last_view_time": datetime.now()
			})


def RemoveLast30minsView():
	cur_date_time = datetime.now()
	for cp_name in CarparkView.keys():
		count = len(CarparkView[cp_name])
		indexes_to_be_removed = []
		for index in range(0, count):
			if (cur_date_time - CarparkView[cp_name][index]["last_view_time"]).total_seconds() / 60 > 30:
				 indexes_to_be_removed.append(index)
		for index in reversed(indexes_to_be_removed):
			CarparkView[cp_name].pop(index)

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
		if len(CarparkHistory) <= 0:
			GrabWeeklyCarparklots()
		#Carpark.GetCarparksTest()
	GrabLatestCarparklots()
	GrabAvgCarparklotsMovement()

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
	RemoveLast30minsView()

def GrabAvgCarparklotsMovement():
	print("GrabAvgCarparklotsMovement")
	if len(CarparkAvgMovement) == 0:
		cur_time = datetime.now().astimezone(pytz.timezone('Asia/Singapore')).replace(minute=0, second=0, microsecond=0)
		HistoryMovement = []
		for i in range(0, 5):
			minutesToRemove = 30 * i
			target_time = cur_time - timedelta(minutes=minutesToRemove)
			data = DataGov.GetCarparkAvailability(target_time.isoformat())
			for cp in data:
				if len(cp['carpark_info']) <= 0:
					continue
				info = cp['carpark_info'][0]
				if cp['carpark_number'] in CarparkAvgMovement.keys():
					CarparkAvgMovement[cp['carpark_number']].append(int(info['lots_available']))
				else:
					CarparkAvgMovement[cp['carpark_number']] = [int(info['lots_available'])]
	else:
		data = DataGov.GetCarparkAvailability(datetime.now().astimezone(pytz.timezone('Asia/Singapore')).isoformat())
		for cp in data:
			if len(cp['carpark_info']) <= 0:
				continue
			info = cp['carpark_info'][0]
			if cp['carpark_number'] in CarparkAvgMovement:
				CarparkAvgMovement[cp['carpark_number']].pop(0)
				CarparkAvgMovement[cp['carpark_number']].append(info['lots_available'])

def GrabWeeklyCarparklots():
	with app.app_context():
		all_carparks = Carpark.GetAllCarparks()
		for cp in all_carparks:
			#logging.info("Prepping " + cp.car_park_no)
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
