from . import db
from geopy import distance

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

	def GetCount():
		return db.session.query(db.func.count(Carpark.car_park_no)).all()[0][0]

	def GetCarparks(long, lat):
		final_list = []
		list = db.session.query(Carpark).all()
		for c in list:
			c.dist = distance.distance((lat, long), (c.lat_coord, c.long_coord)).km
			if c.dist < 5:
				final_list.append(c)
		return final_list
