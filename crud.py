from bson.objectid import ObjectId
from database import flight_collection

from bson.objectid import ObjectId
async def retreive()->list:
    flights = []
    async for fl in flight_collection.find():
        flights.append(fl)
    # print(flights)
    return flights

async def retrive_one(doc) -> dict:
    res = await flight_collection.find_one(doc)
    if res :
        return res
    else :
        return None

async def insert(doc) -> dict:
    res = await flight_collection.insert_many(doc)
    # std = await flight_collection.find_one(res.inserted_id)
    return len(res.inserted_ids)

async def update(id,doc):
    if len(doc)> 1 :
        if await flight_collection.find_one({'_id':ObjectId(id)}) :
            res = await flight_collection.update_one({'_id':ObjectId(id)},{'$set':doc})    
            return await flight_collection.find_one({'_id':ObjectId(id)})
    return None

async def delete(id):
    if await flight_collection.find_one({'_id':ObjectId(id)}):
        res = await flight_collection.delete_one({'_id':ObjectId(id)})   
        return True
    else :
        return False