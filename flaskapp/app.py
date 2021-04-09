from flask import Flask, render_template
import mysql.connector
import sqlalchemy as sqla
from sqlalchemy import create_engine
import pandas as pd
import requests
import json
from datetime import datetime
from os import path

# app is the Flask name
app = Flask(__name__)

from joblib import load

# Homepage on first loading
@app.route("/")
def homepage():
    return render_template("index.html")

# Info page
@app.route("/info")
def info_page():
    return render_template("info.html")

# Route planner page
@app.route("/route")
def route_planner():
    return render_template("route.html")

# '/stations' is the route fetched in initMap() function on index.html page, returns StaticData from database as JSON
@app.route("/stations")
def stations():

    URI = "dublinbikes.chj6z1a17hdc.us-east-1.rds.amazonaws.com"
    PORT = "3306"
    DB = "DublinBikes"
    USER = "admin"
    PASSWORD = "Aws72gene!"

    engine = create_engine("mysql+mysqlconnector://{}:{}@{}:{}/{}".format(USER, PASSWORD, URI, PORT, DB), echo=True)

    print("Connected")
    df = pd.read_sql_table("StaticData", engine)
    #print(df.head())
    #print(df.to_json(orient='records'))
    return df.to_json(orient='records')


# '/bikes' is the route fetched in initMap() function on index.html page, returns AvailableBikes from database as JSON
@app.route("/bikes")
def bikes():

    URI = "dublinbikes.chj6z1a17hdc.us-east-1.rds.amazonaws.com"
    PORT = "3306"
    DB = "DublinBikes"
    USER = "admin"
    PASSWORD = "Aws72gene!"

    engine = create_engine("mysql+mysqlconnector://{}:{}@{}:{}/{}".format(USER, PASSWORD, URI, PORT, DB), echo=True)

    print("Connected")
    df = pd.read_sql_table("AvailableBikes", engine)
    #print(df.head())
    #print(df.to_json(orient='records'))
    return df.to_json(orient='records')

@app.route("/chartW/<int:StationNumber>")
def chartWeekly(StationNumber):
    # get basepath of this file
    basepath = path.dirname(__file__)
    # describe route out of directory to stored dataFrame
    filepath = path.abspath(path.join(basepath, "..", "bikesDataframe.csv"))

    # read in dataframe
    df = pd.read_csv(filepath)
    df['DateTime'] = pd.to_datetime(df['DateTime'])

    # get narrower dataframe with just the chosen station
    station_df = df.loc[df['StationNumber'] == StationNumber]
    # get average per day of week
    week_df = station_df.groupby(['DayOfWeek']).mean()
    # add in day of week as an index so it makes it over in the json object
    week_df['DayOfWeek'] = week_df.index
    return week_df.to_json(orient='records')

@app.route("/chartH/<int:StationNumber>")
def chartHourly(StationNumber):
    # get basepath of this file
    basepath = path.dirname(__file__)
    # describe route out of directory to stored dataFrame
    filepath = path.abspath(path.join(basepath, "..", "bikesDataframe.csv"))

    # read in dataframe
    df = pd.read_csv(filepath)
    df['DateTime'] = pd.to_datetime(df['DateTime'])

    # produces an int value for day of the week
    day_number = datetime.today().weekday()
    # get narrower dataframe with only queried station number on day (of week) of query
    station_df = df.loc[(df['StationNumber'] == StationNumber) & (df['DayOfWeek'] == day_number)]
    # use resample to get each hour averaged out across whole dataframe
    station_df = station_df.set_index('DateTime').resample('1h').mean()
    # groupby each hour of the day, for 24 hours, i.e. 24 rows total
    hourly_df = station_df.groupby(station_df.index.hour).mean()
    # add in index so it carries over to json object
    hourly_df['Hour'] = hourly_df.index
    return hourly_df.to_json(orient='records')

def get_Xnew(hour, day, df):
    df['Date'] = pd.to_datetime(df['Date'])
    df['Hour'] = df['Date'].dt.hour
    df['DayOfWeek'] = df['Date'].dt.dayofweek
    local_df = df.loc[(df['DayOfWeek'] == day) & (df['Hour'] == hour)]

    temp = int(local_df['Temperature'].to_numpy())
    wind = int(local_df['Windspeed'].to_numpy())

    if day == 0:  # if i'ts monday
        array = [0, 0, 0, 0, 0, 0]
    elif day == 1:  # tuesday
        array = [1, 0, 0, 0, 0, 0]
    elif day == 2:  # wednesday
        array = [0, 1, 0, 0, 0, 0]
    elif day == 3:  # thurs
        array = [0, 0, 1, 0, 0, 0]
    elif day == 4:  # fri
        array = [0, 0, 0, 1, 0, 0]
    elif day == 5:  # sat
        array = [0, 0, 0, 0, 1, 0]
    else:  # sun
        array = [0, 0, 0, 0, 0, 1]

    tue = array[0]
    wed = array[1]
    thu = array[2]
    fri = array[3]
    sat = array[4]
    sun = array[5]

    X_new = pd.DataFrame({'FeelsLike': [temp], 'Windspeed': [wind], 'DayOfWeek_1.0': [tue], 'DayOfWeek_2.0': [wed],
                          'DayOfWeek_3.0': [thu], 'DayOfWeek_4.0': [fri], 'DayOfWeek_5.0': [sat],
                          'DayOfWeek_6.0': [sun], 'DateTime': [hour]})
    return X_new

@app.route("/predictBikes/<int:StationNumber>/<int:Day>/<int:Hour>")
def predictBikes(StationNumber, Day, Hour):
    print("trying to connect")
    mydb = mysql.connector.connect(
        host="dublinbikes.chj6z1a17hdc.us-east-1.rds.amazonaws.com",
        user="admin",
        passwd="Aws72gene!",
        database='DublinBikes',
        charset='utf8mb4',
    )
    #mycursor = mydb.cursor(dictionary=False)
    print("Connected")
    #cursor = mydb.cursor()

    # Pandas read sql query
    sql_select_Query = pd.read_sql_query("SELECT Date, Temperature, Windspeed FROM DublinBikes.WeatherForecast48Hour",
                                         mydb)
    # Create a dataframe with all of the rows fetches in the sql query
    df_WF = pd.DataFrame(sql_select_Query, columns=['Date', 'Temperature', 'Windspeed'])

    X_new = get_Xnew(Hour, Day, df_WF)
    models = load('availableBikesModels.joblib')

    return models[StationNumber].predict(X_new)[0]

@app.route("/predictStands/<int:StationNumber>/<int:Day>/<int:Hour>")
def predictStands(StationNumber, Day, Hour):
    print("trying to connect")
    mydb = mysql.connector.connect(
        host="dublinbikes.chj6z1a17hdc.us-east-1.rds.amazonaws.com",
        user="admin",
        passwd="Aws72gene!",
        database='DublinBikes',
        charset='utf8mb4',
    )
    #mycursor = mydb.cursor(dictionary=False)
    print("Connected")
    #cursor = mydb.cursor()

    # Pandas read sql query
    sql_select_Query = pd.read_sql_query("SELECT Date, Temperature, Windspeed FROM DublinBikes.WeatherForecast48Hour",
                                         mydb)
    # Create a dataframe with all of the rows fetches in the sql query
    df_WF = pd.DataFrame(sql_select_Query, columns=['Date', 'Temperature', 'Windspeed'])

    X_new = get_Xnew(Hour, Day, df_WF)
    models = load('availableStandsModels.joblib')

    return models[StationNumber].predict(X_new)[0]

# Just a sample static page for proof of concept
@app.route("/about")
def about():
    return app.send_static_file("about.html")

if __name__ == "__main__":
    app.run(debug=True)


