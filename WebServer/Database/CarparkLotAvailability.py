from . import db

class CarparkLotAvailability(db.Model):
	__tablename__ = 'CarparkLotAvailabilities'
	Id = db.Column(db.Integer, primary_key=True,nullable=False)
	RecordDateId = db.Column(db.Integer, db.ForeignKey('CarparkLotRecordDates.Id'))
	car_park_no = db.Column(db.String(30), db.ForeignKey('Carparks.car_park_no'))
	total_lots = db.Column(db.Integer, nullable=False)
	lots_available = db.Column(db.Integer, nullable=False)
	lot_type = db.Column(db.String(100), nullable=False)
	update_datetime = db.Column(db.DATETIME, nullable=True)

	def __init__(self, RecordDateId, car_park_no, total_lots, lots_available,\
	lot_type, update_datetime):
		self.RecordDateId = RecordDateId
		self.car_park_no = car_park_no
		self.total_lots = total_lots
		self.lots_available = lots_available
		self.lot_type = lot_type
		self.update_datetime = update_datetime

	def Insert(self):
		db.session.add(self)
