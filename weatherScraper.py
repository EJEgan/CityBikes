from sqlalchemy import create_engine
from datetime import datetime
import requests
import json

# For your own personal database, sub in your own details
URI= "dublinbikes.chj6z1a17hdc.us-east-1.rds.amazonaws.com"
PORT="3306"
DB = "DublinBikes"
USER = "admin"
PASSWORD = "Aws72gene!"

engine = create_engine("mysql+mysqlconnector://{}:{}@{}:{}/{}".format(USER, PASSWORD, URI, PORT, DB), echo=True)

# For API req to Open Weather
APIKEY = "f632417a7b24b927a4144dc660501328"
NAME = "dublin,ie"
UNITS = "metric"
WEATHER = "http://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units={}".format(NAME, APIKEY, UNITS)


#making the Current Weather table
sql1 = """
CREATE TABLE IF NOT EXISTS CurrentWeather (
ID INTEGER,
MainDescription VARCHAR(45),
Temperature DECIMAL,
FeelsLike DECIMAL,
WindSpeed DECIMAL,
Time INTEGER,
Day INTEGER,
Date DATE
)
"""

#making the Historical Weather Data table
sql2 = """
CREATE TABLE IF NOT EXISTS HistoricalWeather (
ID INTEGER,
MainDescription VARCHAR(45),
Temperature DECIMAL,
FeelsLike DECIMAL,
WindSpeed DECIMAL,
Time INTEGER,
Day INTEGER,
Date DATE
)
"""

#Execute both SQL statments
try:
    engine.execute(sql1)
    print("Live weather table created")
    engine.execute(sql2)
    print("Historical weather table created")
except Exception as e:
    print("Here is the exception: ", e)

# Get time stamp for beginning of process
now = datetime.now()
current_time = now.strftime("%H%M") #time as a 3-4 sequence of numbers
day = datetime.today().weekday() #produces an int value for day of the week
date = now.strftime("%Y-%m-%d") #probably not going to be used computationally, just for our benefit

# Truncates current weather table and re-populates it with most recent data
def write_to_live(text):
    engine.execute("truncate table CurrentWeather")
    data = json.loads(text)
    vals = (data.get('weather')[0].get('id'), data.get('weather')[0].get('main'),
            data.get('main').get('temp'), data.get('main').get('feels_like'),
            data.get('wind').get('speed'), int(current_time), int(day), date
            )
    print(vals)
    engine.execute("insert into CurrentWeather values(%s,%s,%s,%s,%s,%s,%s,%s)", vals)
    return

# Adds current weather to historical table
def write_to_historical(text):
    data = json.loads(text)
    vals = (data.get('weather')[0].get('id'), data.get('weather')[0].get('main'),
            data.get('main').get('temp'), data.get('main').get('feels_like'),
            data.get('wind').get('speed'), int(current_time), int(day), date
            )
    print(vals)
    engine.execute("insert into HistoricalWeather values(%s,%s,%s,%s,%s,%s,%s,%s)", vals)
    return

#Populate both tables
try:
    r = requests.get(WEATHER)
    text = r.text
    write_to_live(text)
    write_to_historical(text)
    #time.sleep(5*60)
except Exception as e:
    print("Here is the exception: ", e)
