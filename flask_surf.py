import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

# Create a session (link) from Python to the DB
session = Session(engine)


# Flask Setup
app = Flask(__name__)


# Flask Routes

#Home page, with a list all routes that are available.
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to Surfs Up APP API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/about<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/'start_date'                (Please enter start date in format YYYY-MM-DD) <br/> "
        f"/api/v1.0/'start_date'/'end_date'     (Please enter start and date date in format YYYY-MM-DD) <br/>"
    )

#About page describing the excercise 
@app.route("/api/v1.0/about")
def about():
    return (f"Congratulations! I have decided to treat myself to a long holiday vacation in Honolulu, Hawaii after the rigorous Rutgers Data Science BootCamp! <br/>"
    f"To help with my trip planning, I am doing climate analysis of the area."
    f"Pleae use the routes specified to see the queries that I have just developed"
    )

# Convert the query results to a Dictionary using date as the key and prcp as the value.
# Return the JSON representation of the dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Get all dates and precipitation
    prcp_results = session.query(measurement.date, measurement.prcp).all()
    precipitation = []

    for precip in prcp_results:
        precip_dict = {}
        precip_dict["date"] = precip[0]
        precip_dict["prcp"] = precip[1]
        precipitation.append(precip_dict)
    
    return jsonify(precipitation)

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    # Get all stations
    station_results = session.query(station.id, station.station, station.name).all()

    # Create a dictionary from the row data and append to a list of all_passengers
    station_list = []

    for each_station in station_results:
        station_dict = {}
        station_dict["id"] = each_station[0]
        station_dict["station"] = each_station[1]
        station_dict["name"] = each_station[2]
        station_list.append(station_dict)
        
    return jsonify(station_list)


# Query for the dates and temperature observations from a year from the last data point.
# Return a JSON list of Temperature Observations (tobs) for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    # latest date in query 
    date = session.query(measurement.date, measurement.tobs).order_by(measurement.date.desc()).first()
    # get one year back from above date        
    year_ago = dt.datetime.strptime(date[0], "%Y-%m-%d") - dt.timedelta(days=366)

    sel=[measurement.date, measurement.tobs]
    # Query all stations
    tobs_results = session.query(*sel).filter(measurement.date >= year_ago).all()
        
    tobs_list = []
    for each_tobs in tobs_results:
        tobs_dict = {}
        tobs_dict["date"] = each_tobs[0]
        tobs_dict["tobs"] = each_tobs[1]
        tobs_list.append(tobs_dict)
        
    return jsonify(tobs_list)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

@app.route("/api/v1.0/<start>")
def start_date(start=None):
    # return min, average, max temps for all dates >= start date
    sel=[measurement.date, measurement.tobs]
    start_results = session.query(*sel).filter(measurement.date >= start).all()
    print(start_results)
        
    sel = [func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)] 
    station_averages = session.query(*sel).filter(measurement.date >= start).all()
    start_summary = []
    for each_sumry in station_averages:
        smry_dict = {}
        smry_dict["TMIN"] = each_sumry[0]
        smry_dict["TMAX"] = each_sumry[1]
        smry_dict["TAVG"] = each_sumry[2]
        start_summary.append(smry_dict)
           
    return jsonify(start_summary)

# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    # return min, average, max temps for all dates >= start date <= end date
    
    sel=[measurement.date, measurement.tobs]
    start_end_results = session.query(*sel).filter(measurement.date >= start).filter(measurement.date <= end).all()
    print(start_end_results)
    print(start)
    print(end)
        
    sel2 = [func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)] 
    st_end_station_averages = session.query(*sel2).filter(measurement.date >= start).filter(measurement.date <= end).all()
    start_end_summary = []
    for each_sum in st_end_station_averages:
        st_end_sum_dict = {}
        st_end_sum_dict["TMIN"] = each_sum[0]
        st_end_sum_dict["TMAX"] = each_sum[1]
        st_end_sum_dict["TAVG"] = each_sum[2]
        start_end_summary.append(st_end_sum_dict)
    
    return jsonify(start_end_summary)    



if __name__ == '__main__':
    app.run(debug=True)