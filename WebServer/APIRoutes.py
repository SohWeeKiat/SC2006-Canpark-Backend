from flask import Blueprint, request, jsonify
from . import app
from .Database import Carpark
from . import Job
from datetime import datetime, timedelta
import pytz
import json

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
		viewing_now = 0
		if c.car_park_no in Job.CarparkData.keys():
			data = Job.CarparkData[c.car_park_no]
			total_lots = data.total_lots
			lots_available = data.lots_available
			update_datetime = data.update_datetime.isoformat()
		else:
			continue
		if c.car_park_no in Job.CarparkHistory.keys():
			history = Job.CarparkHistory[c.car_park_no]
		if c.car_park_no in Job.CarparkView.keys():
			viewing_now = len(Job.CarparkView[c.car_park_no])

		final_list.append({
			"car_park_no": c.car_park_no,
			"address": c.address,
			"longitude": c.long_coord,
			"latitude": c.lat_coord,
			"total_lots": total_lots,
			"lots_available": lots_available,
			"update_datetime":update_datetime,
			"free_parking": c.free_parking,
			"night_parking": c.night_parking,
			"viewing_now": viewing_now,
			"dist":c.dist,
			"history": history
		})
	#final_list.sort(key=lambda x: x["dist"])
	#return jsonify(final_list)
	return json.dumps(final_list, separators=(',', ':'))

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

@api_bp.route('/ViewCarpark', methods=['POST'])
def ViewCarpark():
	IP = request.headers.get('CF-Connecting-IP')
	content = request.get_json()
	if "UUID" not in content or content["UUID"] is None:
		return jsonify({
			"status":1,
			"Error":"UUID is empty"
		})
	elif "car_park_no" not in content or content["car_park_no"] is None:
		return jsonify({
			"status":2,
			"Error":"car_park_no is empty"
		})
	#elif IP is None or len(IP) <= 0:
		#return jsonify({
			#"status":4,
			#"Error":"cf not working"
		#})
	c = Carpark.GetCarpark(content["car_park_no"])
	if c is None:
		return jsonify({
			"status":3,
			"Error":"Invalid car_park_no"
		})
	Job.InsertCarparkView(content["car_park_no"], content["UUID"])
	return jsonify({
		"status":0
	})
