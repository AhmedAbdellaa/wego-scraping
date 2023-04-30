from fake_useragent import UserAgent
from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
import time
from selenium.webdriver.common.by import By
import re

def get_user_agent():
    return UserAgent(verify_ssl=False)

def clean_duration(duration_str:str):
        '''
        take duration in string 13h 10m via KWI  format and return total duration time in minutes
        '''
        hours = 0
        minutes=0
        try:
            hours = int(re.findall('[0-9]+h',duration_str)[0][:-1])
            minutes = int(re.findall('[0-9]+m',duration_str)[0][:-1])
        # print(hours,minutes)
        finally:
            return hours*60 + minutes
        
def datetime_timezone(date_str:str,time_str:str):
    '''
    time_str :CAI 10:40
    date_str:Mon, 1 Jan
    return  dict of dict_time and time zone
    '''
    time_list = time_str.split(' ')
    return{'datetime':date_str+', '+time_list[1],'time_zone':time_list[0]}

def seg_datetime_timezone(date_time:str,airport:str):
    '''
    date_time :'12 Apr\n22:20'
    airport : KWI Kuwait Airport 
    return  dict of dict_time and time zone , airport
    '''
    port = airport.split(' ')
    date_time = date_time.split('\n')
    
    return{'datetime':date_time[0]+', '+date_time[1],'time_zone':port[0]} , ' '.join(port[1:]).strip()

@dataclass
class Scrapper:
    
    url: str
    endless_scroll : bool = False
    endless_scroll_time : int = 5
    driver :WebDriver = None
    def get_driver(self):
        if self.driver is None :
            UserAgent = get_user_agent()
            options = Options()
            options.add_argument("--no-sandbox")
            # options.add_argument("--headless") #dont open chrome page
            options.add_argument(f"user-agent={UserAgent}")#  user-agent is a string that provides information about the user's browser and their environment

            self.driver = webdriver.Chrome(r"C:\Users\ahmed\Downloads\chromedriver_win32 (1)\chromedriver.exe",options=options)
            # self.driver.maximize_window()
        return self.driver

    def get(self):
        if not self.driver:
            self.get_driver()
        
        self.driver.get(self.url)
        if self.endless_scroll :
            
            current_height = self.driver.execute_script('return document.body.scrollHeight')

            while True :
                self.driver.execute_script('return window.scrollTo(0, document.body.scrollHeight)')
                iter_height = self.driver.execute_script('return document.body.scrollHeight')
                time.sleep(self.endless_scroll_time)
                if(iter_height == current_height):
                    break 
                current_height = iter_height

        return self.driver
    
    
        
    def scrap_flight_cards(self,maxca=10):
        self.get()
        time.sleep(2)
        def set_curr_usd():
            #set concurency to usd 
            #click on country

            curr_title = self.driver.find_element(By.ID,'app').shadow_root.\
            find_element(by=By.ID,value='header').shadow_root.\
            find_element(by=By.CLASS_NAME,value='container').\
            find_element(by=By.TAG_NAME,value='wego-dropdown-settings').shadow_root
            
            curr_title.find_element(By.ID,'country').click()
            time.sleep(1)
            curr_title.find_element(By.ID,'country').click()
            curr_title_in = curr_title.find_element(By.CLASS_NAME,'header-button').find_element(By.TAG_NAME,'wego-dropdown-settings-popup').shadow_root
            curr_title_in.find_element(By.CLASS_NAME,'display-toggle').click()#.find_element(By.CLASS_NAME,'display-toggle').click()
            # time.sleep(1)
            # curr_title.find_element(By.ID,'currency').click()
            curr = curr_title_in.find_element(by=By.ID,value='currency').find_elements(by=By.CLASS_NAME,value='option')

            # find_element(by=By.TAG_NAME,value='wego-dropdown-settings-popup').shadow_root.\
            # find_element(By.ID,'currency').
            for c in curr:
                if c.find_element(by=By.CLASS_NAME,value='option-code').text == "USD" :
                    self.driver.execute_script('return arguments[0].scrollIntoView()',c)
                    c.click()
                    break
            curr_title.find_element(By.ID,'country').click()
        set_curr_usd()
       
        time.sleep(2)
        listview = self.driver.find_element(by=By.ID,value='app').\
            shadow_root.find_element(by=By.ID,value='flights-search').shadow_root.\
            find_element(by=By.ID,value='flightResultList').shadow_root.\
            find_element(by=By.ID,value='listview')
        
        height_1 = -1
        height = 0#0
        idx = 1
        countt= 0
        flight_card_list = []
        while height_1 <height :
            
            height_1 = height
            groupslist = listview.find_elements(by=By.CLASS_NAME,value='group')
            self.driver.execute_script('return arguments[0].scrollIntoView()',groupslist[idx])
            height = int(re.findall('[0-9]+px',groupslist[idx].get_attribute('style'))[1][:-2])
            card_result = self.scrap_flight_card(groupslist[idx])
            if card_result:
                flight_card_list.append(card_result)
            if countt >= maxca :
                return flight_card_list
            else :
                countt += 1
            
            if idx != len(groupslist)-1 :
                idx += 1
            else :
                idx = 0
        # self.driver.close()
        return flight_card_list
    
    def scrap_flight_card(self,card_group):
        
        try :
            
            #price 
            # print(card_group)
            price = card_group.find_element(by=By.TAG_NAME,value='flight-card').shadow_root.\
                find_element(by=By.CLASS_NAME,value='card-price').\
                find_element(by=By.TAG_NAME,value='wego-price').shadow_root.\
                find_element(by=By.CLASS_NAME,value='amount').get_attribute('textContent')
            flight_company = card_group.find_element(by=By.TAG_NAME,value='flight-card').shadow_root.\
                find_element(by=By.CLASS_NAME,value='description').\
                find_element(by=By.TAG_NAME,value='strong').text
            #open flight details
            card_group.find_element(by=By.TAG_NAME,value='flight-card').shadow_root.\
                    find_element(by=By.CLASS_NAME,value='card-actions').click()
            time.sleep(1)
            #scrap flight details
            flightpop = self.driver.find_element(by=By.ID,value='app').\
                shadow_root.find_element(by=By.ID,value='flights-search').shadow_root.\
                find_element(by=By.ID,value='popupCont').find_element(by=By.ID,value='detail').shadow_root
            #flight main details
            flight_panel =  flightpop.find_element(by=By.ID,value='itinerary').\
                find_element(by=By.TAG_NAME,value='flight-detail-itinerary-summary').shadow_root.\
                find_element(by=By.ID,value='panel')
            #flight route
            flight_details = flightpop.find_element(by=By.ID,value='itinerary').\
                find_element(by=By.TAG_NAME,value='flight-detail-itinerary-details').shadow_root.\
                find_elements(by=By.CLASS_NAME,value="segment")
            #expand details 
            flightpop.find_element(by=By.ID,value='itinerary').\
                find_element(by=By.TAG_NAME,value='wego-icon').click()
            time.sleep(1)

            timee=flight_panel.find_elements(By.CLASS_NAME,'airport-code')
            airport= flight_panel.find_elements(By.CLASS_NAME,'airport-name')
            datee = flight_panel.find_elements(By.XPATH,'./div/div/div/div[@class="date"]')
            #0 departure, 1 arrival
            # print('dateeee',airport[0].get_attribute('textContent'))
            duration = flight_panel.find_element(By.CLASS_NAME,'duration').text
            
            description = flight_panel.find_elements(By.XPATH,'./div/div[@class="sub-info"]/div/div[@class="description"]')
            if description :
                descriptions = flight_panel.find_elements(By.XPATH,'./div/div[@class="sub-info"]/div/div[@class="description"]/span')
                description = [ds.get_attribute('textContent') for ds in descriptions]

            else:
                description = []
            flight_card = {"flight_company":flight_company, 
                        "flight_price":float(price),
                        "flight_duration":clean_duration(duration),
                        "leave_datetime":datetime_timezone(datee[0].get_attribute('textContent'),timee[0].get_attribute('textContent')),
                        "arrive_time":datetime_timezone(datee[1].get_attribute('textContent'),timee[1].get_attribute('textContent')),
                        "leave_airport":airport[0].text,
                        "arrive_airport":airport[1].text ,
                        "description":description}

            segsList =[]
            for seg in flight_details:
                seg_airports=[ap.text  for ap in seg.find_elements(by=By.CLASS_NAME,value="airport") if ap.text !='']
                seg_datetimes=[ap.text  for ap in seg.find_elements(by=By.CLASS_NAME,value="datetime") if ap.text !='']
                seg_duration = [ap.text  for ap in seg.find_elements(by=By.CLASS_NAME,value="duration") if ap.text !='']
                seg_flightCompany=[ap.text  for ap in seg.find_elements(by=By.XPATH,value='./div/div[@class="info"]/span') if ap.text !='']
                seg_meta = [ap.text  for ap in seg.find_elements(by=By.CLASS_NAME,value="meta") if ap.text !='']
                # print(seg_meta)
                # print(seg_duration)
                # print(seg_flightCompany)

                for idx,_ in enumerate(seg_airports):
                    airport_dattime = seg_datetime_timezone(seg_datetimes[idx],seg_airports[idx])
                    seg_dict = {
                                    "airport":airport_dattime[1],
                                    "datetime":airport_dattime[0],
                                    "durtion":clean_duration(seg_duration[0]),
                                    "flight_company":seg_flightCompany[0] ,
                                    "meta":seg_meta[0]
                        }
                    segsList.append(seg_dict)
            
                flight_card.update({"flight_details": segsList})
                        
            #close flight card details
            flightpop.find_element(By.ID,'header').find_element(By.CLASS_NAME,'close').click()
            # flightpop.find_element(By.ID,'header').find_element(By.CLASS_NAME,'close').click()
            # time.sleep(20)
            
            return flight_card

        except: 
            print(card_group.get_attribute('style'))
            return False

    