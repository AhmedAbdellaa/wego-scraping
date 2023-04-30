import uvicorn
from typing import Any
from fastapi import FastAPI
import schemas
import crud
from typing import List
import worker
from scrapper import Scrapper

app = FastAPI()


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app!"}

@app.get('/flights',response_model=List[schemas.FlightScheama])
async def get_flights() -> Any:
    return await crud.retreive()#{"message": "Welcome to this fantastic app!"}

@app.post('/scrapDB')
async def scrap_toDB(req:schemas.ScrapFlighIn):
    print(req)
    worker.scrap_flights.delay(**dict(req))
    return {"message":"scrap command was sent and will add asap to mongo db"}

@app.post('/scrap',response_model=List[schemas.FlightScheama])
async def scrap(req:schemas.ScrapFlighIn):
    s = Scrapper(f'https://eg.wego.com/en/flights/searches/c{req.cfrom}-c{req.cto}-{req.fdate}/{req.fclass}/{req.adult}a:{req.childs}c:{req.infants}i')
    data = s.scrap_flight_cards(req.snflight)
    return data



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5050, reload=True)