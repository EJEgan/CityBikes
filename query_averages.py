import mysql.connector
import pandas as pd
import requests
import json
from datetime import datetime


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

cursor = mydb.cursor()

#Pandas read sql query
sql_select_Query = pd.read_sql_query("SELECT DayOfWeek, StationName, Time, AvailableBikes FROM DublinBikes.LiveHistoricalData", mydb)

#Create a dataframe with all of the rows fetches in the sql query
df = pd.DataFrame(sql_select_Query, columns=['DayOfWeek', 'StationName', 'Time', 'AvailableBikes'])


#Group by Station name, day of week, time. (This will be the key for your query to the json object)
mean_bikes = df.groupby(["StationName","DayOfWeek","Time"]).mean()

#Print out result
#print(mean_bikes)


#Save to Json file (oriented by index)
result = mean_bikes.to_json(r'mean_bikes.json',orient="index")


"""BELOW IS A SAMPLE QUERY TO THE JSON OBJECT. THIS IS WHAT YOU WILL NEED ON FLASK.
 It queries the key - station, day number, time. The value to this key will be the AVERAGE available bikes
 For example, will return average bikes for Avondale Road station on day 2 at 1225
"""
# with open('mean_bikes.json') as json_file:
#     data = json.load(json_file)
#     print(data["('AVONDALE ROAD', 2, 1225)"])



















