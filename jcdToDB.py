import mysql.connector
import requests
import json
from datetime import datetime

#Connect to Database
try:
    print("trying to connect")
    mydb = mysql.connector.connect(
        host="dublinbikes.chj6z1a17hdc.us-east-1.rds.amazonaws.com",
        user="admin",
        passwd="Aws72gene!",
        database='DublinBikes',
        charset='utf8mb4',
    )
    mycursor = mydb.cursor(dictionary=False)

    print("Connected")

    APIKEY = "feb8a7c42cb881254b40b7ca5bc99f38e8c606b0"
    NAME = "dublin"
    STATIONS = "https://api.jcdecaux.com/vls/v1/stations"

    r = requests.get(STATIONS, params={"apiKey": APIKEY, "contract": NAME})

# Use same time value for all entries in database
    now = datetime.now()
    current_time = now.strftime("%H%M") #time as a 3-4 sequence of numbers
    day = datetime.today().weekday() #produces an int value for day of the week
    date = now.strftime("%Y-%m-%d") #probably not going to be used computationally, just for our benefit

# Add bike data into long-term repository
    def live_to_historical(text):
        stations = json.loads(text)
        for station in stations:
            vals = (int(station.get('number')), station.get('name'),
                    int(station.get('bike_stands')), int(station.get('available_bike_stands')),
                    int(station.get('available_bikes')), station.get('status'),
                    int(current_time), int(day), date
                    )
            mycursor.execute("insert into LiveHistoricalData values(%s,%s,%s,%s,%s,%s,%s,%s,%s)", vals)
            mydb.commit()
        return

# Replace bike data in live table
    def replace_live_data(text):
        mycursor.execute("truncate table AvailableBikes")
        mydb.commit()
        stations = json.loads(text)
        for station in stations:
            vals = (int(station.get('number')), station.get('name'),
                    int(station.get('bike_stands')), int(station.get('available_bike_stands')),
                    int(station.get('available_bikes')), station.get('status'),
                    int(current_time), int(day), date
                    )
            mycursor.execute("insert into AvailableBikes values(%s,%s,%s,%s,%s,%s,%s,%s,%s)", vals)
            mydb.commit()
        return

    live_to_historical(r.text)
    print("Historical DB updated")
    replace_live_data(r.text)
    print("Live table updated")
    mydb.close()
except Exception as e:
    print(e)