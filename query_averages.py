import mysql.connector
import pandas as pd


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
sql_select_Query = pd.read_sql_query("SELECT DayOfWeek, StationNumber, Time, Date, AvailableBikes, AvailableBikeStands FROM DublinBikes.LiveHistoricalData ORDER BY Date DESC LIMIT 400000", mydb)

#Create a dataframe with all of the rows fetches in the sql query
df = pd.DataFrame(sql_select_Query, columns=['DayOfWeek', 'StationNumber', 'Time', 'Date', 'AvailableBikes', 'AvailableBikeStands'])

# Convert time stored as integer to pandas timedelta
dt = df['Time']
df['NumericTime'] =(pd.to_timedelta(dt//100, unit='H') + pd.to_timedelta(dt % 100, unit = 'T'))

# Remove timedelta prefix so that strings can be combined to form date time
df['NumericTime'] = df['NumericTime'].astype("string")
df['NumericTime'] = df['NumericTime'].str.slice(start=6, stop=15)

# Recategorize date as a string, combine with time, create datetime column
df['Date'] = df['Date'].astype("string")
df['DateTime'] = df['Date'] + df['NumericTime']
df['DateTime'] = pd.to_datetime(df['DateTime'])

# Select necessary columns to take forward
df_w_datetime = df[['DayOfWeek', 'StationNumber', 'AvailableBikes', 'AvailableBikeStands', 'DateTime']]

# Save to csv file (smaller than JSON file)
csv = df_w_datetime.to_csv("bikesDataframe.csv", index = False)

















