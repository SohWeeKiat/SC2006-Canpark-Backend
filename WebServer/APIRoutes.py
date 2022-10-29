from flask import Blueprint, request, jsonify
from . import app
from .Database import Carpark
from . import Job
from datetime import datetime, timedelta
import pytz

api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/GetCarparks', methods=['GET'])
def GetCarparks():
	args = request.args
	long = args.get("long", default=None, type=float)
	lat = args.get("lat", default=None, type=float)
	if long == None or lat == None:
		return "test"
	cp = Carpark.GetCarparks(long, lat)
	final_list = []
	counter = 0
	cp.sort(key=lambda x: x.dist)
	for c in cp:
		total_lots = 0
		lots_available = 0
		update_datetime = ""
		history_dates = []
		if c.car_park_no in Job.CarparkData.keys():
			data = Job.CarparkData[c.car_park_no]
			total_lots = data.total_lots
			lots_available = data.lots_available
			update_datetime = data.update_datetime.isoformat()
		else:
			continue
		history = {}
		if c.car_park_no in Job.CarparkHistory.keys():
			history = Job.CarparkHistory[c.car_park_no]
		final_list.append({
			"car_park_no": c.car_park_no,
			"address": c.address,
			"longitude": c.long_coord,
			"latitude": c.lat_coord,
			"total_lots": total_lots,
			"lots_available": lots_available,
			"update_datetime":update_datetime,
			"dist":c.dist,
			"history": history
		})
	#final_list.sort(key=lambda x: x["dist"])
	return jsonify(final_list)

@api_bp.route('/GetCarparkHistory', methods=['GET'])
def GetCarparkHistory():
	args = request.args
	car_park_no = args.get("id", default=None, type=str)
	c = Carpark.GetCarpark(car_park_no)
	if c is not None:
		history_hours, history_data = c.GetPast7DaysSlots()
		return jsonify({
			"hours":history_hours,
			"data":history_data
		})
	else:
		return jsonify({
			"hours":[],
			"data":[]
		})
