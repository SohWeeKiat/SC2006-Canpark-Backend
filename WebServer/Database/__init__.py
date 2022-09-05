from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session

db = SQLAlchemy()
session = Session()
from .Carpark import Carpark
from .CarparkLotAvailability import CarparkLotAvailability
from .CarparkLotRecordDate import CarparkLotRecordDate
