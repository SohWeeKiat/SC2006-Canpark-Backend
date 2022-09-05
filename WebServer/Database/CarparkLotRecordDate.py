from . import db

class CarparkLotRecordDate(db.Model):
	__tablename__ = 'CarparkLotRecordDates'
	Id = db.Column(db.Integer, primary_key=True,nullable=False)
	RecordDate = db.Column(db.DATETIME, nullable=True)

	def __init__(self, RecordDate):
		self.RecordDate = RecordDate

	def Insert(self):
		db.session.add(self)
		db.session.commit()

	def GetCount():
		return db.session.query(db.func.count(CarparkLotRecordDate.Id)).all()[0][0]
