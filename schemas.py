from typing import Optional,Union,List
from pydantic import Field,BaseModel

class InnerFlightSchema(BaseModel) : 
    airport : str
    datetime : dict
    durtion : int
    flight_company : str 
    meta : str
class FlightScheama(BaseModel)  : 
    flight_company : str 
    flight_price : float
    flight_duration : int
    leave_datetime : dict
    arrive_time : dict
    leave_airport : str
    arrive_airport : str 
    description : List[str]
    flight_details : Optional[List[InnerFlightSchema]] 

class ScrapFlighIn(BaseModel):
    cfrom:str
    cto:str
    fdate:str
    fclass:str = Field(default='economy')
    adult:int = Field(default=1)
    childs:int = Field(default=0)
    infants:int = Field(default=0)
    snflight:int = Field(default=10,description="number of flights to scrap")