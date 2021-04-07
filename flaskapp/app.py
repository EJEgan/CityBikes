from flask import Flask, render_template
import mysql.connector
import sqlalchemy as sqla
from sqlalchemy import create_engine
import pandas as pd
import requests
import json
from datetime import datetime
from os import path

# Followed Aonghus precisely as I could, so app is the Flask name
app = Flask(__name__)

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


# Just a sample static page for proof of concept
@app.route("/about")
def about():
    return app.send_static_file("about.html")

if __name__ == "__main__":
    app.run(debug=True)


