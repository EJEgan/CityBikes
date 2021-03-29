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
sql_select_Query = pd.read_sql_query("SELECT DayOfWeek, StationNumber, Time, Date, AvailableBikes, AvailableBikeStands FROM DublinBikes.LiveHistoricalData", mydb)

#Create a dataframe with all of the rows fetches in the sql query
df = pd.DataFrame(sql_select_Query, columns=['DayOfWeek', 'StationNumber', 'Time', 'Date', 'AvailableBikes', 'AvailableBikeStands'])

print(df.head(3))
# Convert time stored as integer to pandas timedelta
dt = df['Time']
df['NumericTime'] =(pd.to_timedelta(dt//100, unit='H') + pd.to_timedelta(dt % 100, unit = 'T'))

# Remove timedelta prefix so that strings can be combined to form date time
df['NumericTime'] = df['NumericTime'].astype("string")
df['NumericTime'] = df['NumericTime'].str.slice(start=6, stop=15)
print("1 \n", df.head(3))

# Recategorize date as a string, combine with time, create datetime column
df['Date'] = df['Date'].astype("string")
df['DateTime'] = df['Date'] + df['NumericTime']
print("2 \n", df.head(3))
df['DateTime'] = pd.to_datetime(df['DateTime'])
print("3 \n", df.head(3))

# Select necessary columns to take forward
df_w_datetime = df[['DayOfWeek', 'StationNumber', 'AvailableBikes', 'AvailableBikeStands', 'DateTime']]

# Save to csv file (smaller than JSON file)
csv = df_w_datetime.to_csv("bikesDataframe.csv", index = False)

#Group by Station name, day of week, time. (This will be the key for your query to the json object)
#mean_bikes = df.groupby(["StationNumber","DayOfWeek","Time"]).mean()

#Print out result
#print(mean_bikes)


#Save to Json file (oriented by index)
#result = mean_bikes.to_json(r'mean_bikes.json',orient="index")


"""BELOW IS A SAMPLE QUERY TO THE JSON OBJECT. THIS IS WHAT YOU WILL NEED ON FLASK.
 It queries the key - station, day number, time. The value to this key will be the AVERAGE available bikes
 For example, will return average bikes for Avondale Road station on day 2 at 1225
"""
# with open('mean_bikes.json') as json_file:
#     data = json.load(json_file)
#     print(data["('AVONDALE ROAD', 2, 1225)"])



















