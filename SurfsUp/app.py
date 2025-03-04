# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
base = automap_base()

# reflect the tables
base.prepare(autoload_with=engine)

# Save references to each table
station = base.classes.station
measurement = base.classes.measurement

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
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of data and precipitation scores"""
    # Query
    most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()

    most_recent_date = most_recent_date[0]

    most_recent_date= pd.to_datetime(most_recent_date)
    past_year = most_recent_date - pd.DateOffset(years=1)
    most_recent_date = most_recent_date.date()
    past_year = past_year.date()

    date_prcp = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= past_year, measurement.date <= most_recent_date).all()


    session.close()

    # Create a dictionary
    precipitation = []
    for date, prcp in date_prcp:
        precipitation_dict = {}
        precipitation_dict["Date"] = date
        precipitation_dict["precipitation"] = prcp
        precipitation.append(precipitation_dict)

    return jsonify(precipitation)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations from the dataset"""
    # Query
    most_active_stations = (
        session.query(measurement.station)
        .group_by(measurement.station)
        .order_by(func.count(measurement.station).desc()).all()
    )

    session.close()

    all_stations = list(np.ravel(most_active_stations))


    return jsonify(all_stations)




@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperature observations of the most-active station for the previous year of data"""
    # Query
    most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()

    most_recent_date = most_recent_date[0]

    most_recent_date= pd.to_datetime(most_recent_date)
    past_year = most_recent_date - pd.DateOffset(years=1)
    most_recent_date = most_recent_date.date()
    past_year = past_year.date()

    most_active_stations = (
    session.query(measurement.station, func.count(measurement.station))
    .group_by(measurement.station)
    .order_by(func.count(measurement.station).desc()).all()
    )

    most_active_station_id = most_active_stations[0][0]


    most_active_station_tobs_last12months = session.query(
        measurement.date, measurement.tobs).filter(
        measurement.station == most_active_station_id,
        measurement.date >= past_year , measurement.date <= most_recent_date).all()

    session.close()

    most_active_station_tobs_last12months_json = list(np.ravel(most_active_station_tobs_last12months))

    return jsonify(most_active_station_tobs_last12months_json)



@app.route('/api/v1.0/<start>', methods=['GET'])
def get_temp_start(start):
    session = Session(engine)

    # Query tobs
    tobs_data = (
        session.query(                
            func.min(measurement.tobs),
            func.max(measurement.tobs),
            func.avg(measurement.tobs)
        )
        .filter(measurement.date >= start)
        .all()
    )

    session.close()

    tobs_dict = {
        "Start Date": start,
        "Tobs Min": tobs_data[0][0], 
        "Tobs Max": tobs_data[0][1],  
        "Tobs Avg": tobs_data[0][2]   
    }

    return jsonify(tobs_dict)


@app.route('/api/v1.0/<start>/<end>', methods=['GET'])
def get_temp_range(start, end):
    session = Session(engine)

    # Query tobs
    tobs_data = (
        session.query(                
            func.min(measurement.tobs),
            func.max(measurement.tobs),
            func.avg(measurement.tobs)
        )
        .filter(measurement.date >= start, measurement.date <= end)
        .all()
    )

    session.close()

    tobs_dict = {
        "Start Date": start,
        "End Date": end,
        "Tobs Min": tobs_data[0][0],
        "Tobs Max": tobs_data[0][1], 
        "Tobs Avg": tobs_data[0][2]  
    }

    return jsonify(tobs_dict)



if __name__ == '__main__':
    app.run(debug=True)