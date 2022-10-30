from . import db
from geopy import distance
from sqlalchemy.orm import relationship
from sqlalchemy.orm import lazyload, joinedload,contains_eager
from datetime import datetime, timedelta,timezone
import pytz
from . import CarparkLotRecordDate
from . import CarparkLotAvailability

class Carpark(db.Model):
	__tablename__ = 'Carparks'
	car_park_no = db.Column(db.String(30), primary_key=True,nullable=False)
	address = db.Column(db.String(100), nullable=False)
	x_coord = db.Column(db.Float, nullable=False)
	y_coord = db.Column(db.Float, nullable=False)
	car_park_type = db.Column(db.String(100), nullable=False)
	type_of_parking_system = db.Column(db.String(100), nullable=False)
	short_term_parking = db.Column(db.String(100), nullable=False)
	free_parking = db.Column(db.String(100), nullable=False)
	night_parking = db.Column(db.String(100), nullable=False)
	car_park_decks = db.Column(db.Integer, nullable=False)
	gantry_height = db.Column(db.Integer, nullable=False)
	car_park_basement = db.Column(db.String(100), nullable=False)
	long_coord = db.Column(db.Float, nullable=False)
	lat_coord = db.Column(db.Float, nullable=False)

	carpark_lot_records = relationship("CarparkLotAvailability", back_populates="carpark")

	def __init__(self, car_park_no, address, x_coord, y_coord, car_park_type,\
	type_of_parking_system, short_term_parking, free_parking, night_parking,\
	car_park_decks, gantry_height, car_park_basement, long_coord, lat_coord):
		self.car_park_no = car_park_no
		self.address = address
		self.x_coord = x_coord
		self.y_coord = y_coord
		self.car_park_type = car_park_type
		self.type_of_parking_system = type_of_parking_system
		self.short_term_parking = short_term_parking
		self.free_parking = free_parking
		self.night_parking = night_parking
		self.car_park_decks = car_park_decks
		self.gantry_height = gantry_height
		self.car_park_basement = car_park_basement
		self.long_coord = long_coord
		self.lat_coord = lat_coord
		self.dist = 0

	def Insert(self):
		db.session.add(self)

	def GetPerfectLastDayOfWeek():
		end_date = datetime.now()
		end_date = end_date.astimezone(pytz.timezone('Asia/Singapore'))\
		.replace(hour=0, minute=0, second=0, microsecond=0)
		day_of_week = end_date.weekday()
		if day_of_week != 0:#not sunday
			end_date -= timedelta(days = day_of_week)
		end_date = end_date.astimezone(pytz.UTC)
		return end_date

	def GetPast7DaysSlots(self):
		from . import CarparkLotRecordDate
		from . import CarparkLotAvailability
		sg = pytz.timezone('Asia/Singapore')

		end_date = Carpark.GetPerfectLastDayOfWeek()
		start_date = end_date - timedelta(days=7)

		#list = self.carpark_lot_records\
		#.join(CarparkLotAvailability.RecordDateEntry)\
		#.filter(CarparkLotRecordDate.RecordDate >= start_date,CarparkLotRecordDate.RecordDate <= end_date)\
		#.order_by(CarparkLotRecordDate.RecordDate)\
		#.all()
		list = self.carpark_lot_records
		collection_of_data = []
		collection_of_hours = []
		hours = []
		data = []
		utc=pytz.UTC
		for hour_offset in range(0, 7 * 24):
			start_time = start_date + timedelta(hours=hour_offset)
			end_time = start_time + timedelta(seconds=1)
			if len(data) >= 24:
				collection_of_data.append(data)
				collection_of_hours.append(hours)
				data = []
				hours = []
			added = False
			for e in list:
				utc_dt = utc.localize(e.RecordDateEntry.RecordDate)
				#print(utc_dt.isoformat())
				if utc_dt >= start_time and \
				utc_dt <= end_time:
					hours.append(start_time.astimezone(sg).strftime("%m/%d/%Y, %H:%M:%S"))
					data.append(e.lots_available)
					added = True
					break
			if not added:
				#print("Failed to find " + start_time.isoformat())
				hours.append(start_time.astimezone(sg).strftime("%m/%d/%Y, %H:%M:%S"))
				data.append(0)
		collection_of_data.append(data)
		collection_of_hours.append(hours)
		return collection_of_hours, collection_of_data

	def GetCount():
		return db.session.query(db.func.count(Carpark.car_park_no)).all()[0][0]

	def GetCarparks(long, lat):
		final_list = []
		n_pt = distance.distance(kilometers=5).destination((lat, long), bearing=0)
		east_pt = distance.distance(kilometers=5).destination((lat, long), bearing=90)
		s_pt = distance.distance(kilometers=5).destination((lat, long), bearing=180)
		west_pt = distance.distance(kilometers=5).destination((lat, long), bearing=270)

		list = db.session.query(Carpark)\
		.options(lazyload(Carpark.carpark_lot_records))\
		.filter(Carpark.lat_coord <= n_pt.latitude, Carpark.lat_coord >= s_pt.latitude,Carpark.long_coord >= west_pt.longitude, Carpark.long_coord <= east_pt.longitude)\
		.all()
		for c in list:
			c.dist = distance.distance((lat, long), (c.lat_coord, c.long_coord)).km
			if c.dist < 5:
				final_list.append(c)
		return final_list

	def GetAllCarparks():
		from . import CarparkLotRecordDate
		from . import CarparkLotAvailability
		end_date = Carpark.GetPerfectLastDayOfWeek() + timedelta(days=1)
		start_date = end_date - timedelta(days=9)#buffer 2 days
		return db.session.query(Carpark).join(Carpark.carpark_lot_records)\
		.join(CarparkLotAvailability.RecordDateEntry)\
		.options(contains_eager("carpark_lot_records")).filter(CarparkLotRecordDate.RecordDate >= start_date,\
		CarparkLotRecordDate.RecordDate <= end_date).all()

	def GetCarpark(id):
		return db.session.query(Carpark).options(lazyload(Carpark.carpark_lot_records))\
		.filter(Carpark.car_park_no == id).one()

	def GetCarparksTest():
		print(datetime.now())
		list = db.session.query(Carpark).options(lazyload(Carpark.carpark_lot_records)).all()
		print(datetime.now())
		list[0].GetPast7DaysSlots()
