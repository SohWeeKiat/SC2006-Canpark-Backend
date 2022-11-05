
class Config:
	SQLALCHEMY_DATABASE_URI = "sqlite:///webdb.db"
	JOBS = [
        {
            'id': 'InitializeDB',
            'func': 'WebServer.Job:InitializeDB',
            'args': (),
            'trigger': 'date',
        },
		{
            'id': 'GrabLatestCarparklots',
            'func': 'WebServer.Job:GrabLatestCarparklots',
            'args': (),
            'trigger': 'interval',
            'seconds': 60
        },
		{
            'id': 'GrabAvgCarparklotsMovement',
            'func': 'WebServer.Job:GrabAvgCarparklotsMovement',
            'args': (),
            'trigger': 'interval',
            'minutes': 30
        }
    ]
	SCHEDULER_API_ENABLED = True
	CarparkInfo_URL = "https://data.gov.sg/api/action/datastore_search?resource_id=139a3035-e624-4f56-b63f-89ae28d4ae4c&limit=10000"
	CarparkAvail_URL = "https://api.data.gov.sg/v1/transport/carpark-availability"
	OneMapConvertSVY21_WGS84 = "https://developers.onemap.sg/commonapi/convert/3414to4326"
