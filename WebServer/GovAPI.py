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
		print(resp)
		if len(resp["items"]) <= 0:
			return []
		return resp['items'][0]['carpark_data']
