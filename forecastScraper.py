from sqlalchemy import create_engine
from datetime import datetime
import requests
import json
import pandas as pd

# For your own personal database, sub in your own details
URI= "dublinbikes.chj6z1a17hdc.us-east-1.rds.amazonaws.com"
PORT="3306"
DB = "DublinBikes"
USER = "admin"
PASSWORD = "Aws72gene!"

engine = create_engine("mysql+mysqlconnector://{}:{}@{}:{}/{}".format(USER, PASSWORD, URI, PORT, DB), echo=True)

# For API req to Open Weather
APIKEY = "f632417a7b24b927a4144dc660501328"
LAT = "53.35"
LON = "-6.26"
EXCLUDE = "current,minutely,daily,alerts"
UNITS = "metric"
WEATHER = "https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude={}&units={}&appid={}".format(LAT, LON, EXCLUDE, UNITS, APIKEY)


#making the WeatherForecast table
sql = """
CREATE TABLE IF NOT EXISTS WeatherForecast48Hour (
Date DATETIME,
ID INTEGER,
MainDescription VARCHAR(45),
Temperature DECIMAL,
FeelsLike DECIMAL,
WindSpeed DECIMAL
)
"""

#Execute both SQL statments
try:
    engine.execute(sql)
    print("Live weather table created")
except Exception as e:
    print("Here is the exception: ", e)


# Truncates current weather table and re-populates it with most recent data
def write_to_forecast(text):
    engine.execute("truncate table WeatherForecast48Hour")
    data = json.loads(text)
    hours = data.get('hourly')[0]
    print(hours)
    for i in range(len(data.get('hourly'))):
        # turn the API's date value into datetime
        timeStamp = datetime.utcfromtimestamp(data.get('hourly')[i].get('dt')).strftime('%Y-%m-%d %H:%M:%S')
        # get a row's worth of data
        vals = (timeStamp, data.get('hourly')[i].get('weather')[0].get('id'),
                data.get('hourly')[i].get('weather')[0].get('main'),
                data.get('hourly')[i].get('temp'), data.get('hourly')[i].get('feels_like'),
                data.get('hourly')[i].get('wind_speed')
                )
        print(vals)
        # add to the database
        engine.execute("insert into WeatherForecast48Hour values(%s,%s,%s,%s,%s,%s)", vals)
    return

#Populate the table
try:
    r = requests.get(WEATHER)
    text = r.text
    print(text)
    write_to_forecast(text)
except Exception as e:
    print("Here is the exception: ", e)
