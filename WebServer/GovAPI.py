import requests
import Config

#print(Config.Config.CarparkInfo_URL)
class DataGov:
	def GetCarparkList():
		resp = requests.get(Config.Config.CarparkInfo_URL).json()
		if not resp["success"]:
			return []
		print(resp["result"]["records"])
		return resp["result"]["records"]

	def GetCarparkAvailability(timestamp):
		resp = requests.get(Config.Config.CarparkAvail_URL, params=\
		{'date_time': timestamp}).json()
		if 'items' not in resp.keys():
			print(f"Failed to get data for {timestamp}, retrying")
			return DataGov.GetCarparkAvailability(timestamp)
		elif len(resp["items"]) <= 0:
			return []
		return resp['items'][0]['carpark_data']

	def ConvertSVY21_WGS84(X, Y):
		resp = requests.get(Config.Config.OneMapConvertSVY21_WGS84,params=\
		{'X': X, 'Y': Y}).json()
		print(resp)
		return resp["latitude"], resp["longitude"]
