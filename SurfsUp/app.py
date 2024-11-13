# Import the dependencies.
from flask import Flask, jsonify
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:////Users/Jean/Documents/Bootcamp/sqlalchemy-challenge/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base

# reflect the tables
Base.prepare(autoload_with=engine)


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return( f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        f"<p>Format start and end date as MMDDYYYY. </p>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Recycled first section of code from the jupyter notebook file.
    # Design a query to retrieve the last 12 months of precipitation data and plot the results. 
    # Starting from the most recent data point in the database. 
    latest_date = dt.date(2017, 8, 23)

    # Calculate the date one year from the last date in data set.
    query_date = latest_date - dt.timedelta(days=365)

    # Query the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= query_date).all()

    # Create a dictionary from the query results
    precipitation_by_date = {date: prcp for date, prcp in results}
    
    return jsonify(precipitation_by_date)


@app.route("/api/v1.0/stations")
def stations():
    # Query all stations from the dataset
    results = session.query(Station.station).all()

    # Create a list of all stations
    stations_list = [station[0] for station in results]

    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    # Recycled first part of code from Jupyter notebook
    # Define the latest date in the dataset
    latest_date = dt.date(2017, 8, 23)

    # Calculate the date one year from the last date in the dataset
    query_date = latest_date - dt.timedelta(days=365)

    # Perform a query to retrieve the temperature observations for the most active station
    temp_results = session.query(Measurement.tobs). \
        filter(Measurement.date >= query_date). \
        filter(Measurement.station == 'USC00519281'). \
        all()

    # Create a list of temperature observations
    temps_list = [temp[0] for temp in temp_results]  # Extracting the temperature values

    return jsonify(temps_list)

@app.route("/api/v1.0/<start>")
def start(start):
    # Convert the start date from string to date object
    start_date = dt.datetime.strptime(start, '%m%d%Y').date()

    # Query for TMIN, TAVG, and TMAX for all dates greater than or equal to start date
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start_date).all()

    # Create a dictionary to hold the results
    temp_stats = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }

    return jsonify(temp_stats)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Convert the start and end dates from string to date objects
    start_date = dt.datetime.strptime(start, '%m%d%Y').date()
    end_date = dt.datetime.strptime(end, '%m%d%Y').date()

    # Query for TMIN, TAVG, and TMAX for the date range
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    # Create a dictionary to hold the results
    temp_stats = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }

    return jsonify(temp_stats)


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)