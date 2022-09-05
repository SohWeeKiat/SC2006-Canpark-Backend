from datetime import datetime
from .Database.Carpark import Carpark
from .Database.CarparkLotRecordDate import CarparkLotRecordDate
from .Database.CarparkLotAvailability import CarparkLotAvailability
from .Database import db
from . import app
from .GovAPI import DataGov
from datetime import datetime, timedelta

def InitializeDB():
	with app.app_context():
		if Carpark.GetCount() <= 0:
			carparks = DataGov.GetCarparkList()
			for carpark in carparks:
				cp = Carpark(carpark['car_park_no'], carpark['address'],
					carpark['x_coord'], carpark['y_coord'],
					carpark['car_park_type'], carpark['type_of_parking_system'],
					carpark['short_term_parking'], carpark['free_parking'],
					carpark['night_parking'], carpark['car_park_decks'],
					carpark['gantry_height'], carpark['car_park_basement'])
				cp.Insert()
			db.session.commit()
		if CarparkLotRecordDate.GetCount() <= 0:
			cur_date_time = datetime.now()
			cur_date_time = cur_date_time.replace(minute=0, second=0)
			for past_hr in range(0, 3 * 24):
				record_date = CarparkLotRecordDate(cur_date_time)
				record_date.Insert()
				data = DataGov.GetCarparkAvailability(cur_date_time.isoformat())
				for cp in data:
					if len(cp['carpark_info']) <= 0:
						continue
					info = cp['carpark_info'][0]
					cpa = CarparkLotAvailability(record_date.Id, cp['carpark_number'],
					info['total_lots'], info['lots_available'], info['lot_type'],
					datetime.fromisoformat(cp['update_datetime']))
					cpa.Insert()
				cur_date_time -= timedelta(hours=1)
			db.session.commit()
