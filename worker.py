from celery import Celery
from celery.schedules import crontab
from celery.signals import(
     beat_init # for scheduling taskes
     ,worker_process_init)

from scrapper import Scrapper
import crud 

import asyncio

celery_app  = Celery(__name__)

REDIS_URL = "redis://localhost:6379/0"
celery_app.conf.broker_url= REDIS_URL
celery_app.conf.result_backend = REDIS_URL


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender,*args,**kwargs):
    sender.add_periodic_task(
        crontab(minute='*/5'),
        scrap_flights.s()
    )
                         

def celery_on_startup(*args,**kwargs):
    print("hello world")

beat_init.connect(celery_on_startup)
worker_process_init.connect(celery_on_startup)

@celery_app.task
def random_task(name,age):
    print(f'who throws a showe. Honestly {name}')

@celery_app.task
def scrap_flights(cfrom:str,cto:str,fdate:str,fclass:str,adult:int,childs:int,infants:int,snflight:int):
    # print("heooooo",cfrom)
    s = Scrapper(f'https://eg.wego.com/en/flights/searches/c{cfrom}-c{cto}-{fdate}/{fclass}/{adult}a:{childs}c:{infants}i')
    data = s.scrap_flight_cards(snflight)
    # print("doing scraping")
    ins =  asyncio.get_event_loop().run_until_complete(crud.insert(data))
    # ins = crud.insert(data)

    if ins > 0 :
        return True
    else :
        return False

#celery --app worker.celery_app worker --loglevel INFO

#celery --app worker.celery_app worker --beat --loglevel INFO