# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False}, echo=True)

# reflect an existing database into a new model
Base = automap_base()


# reflect the tables
Base.prepare(autoload_with=engine)


# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

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
    """API Routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"        
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"For the following, please input a date where indicated:<br/>"       
        f"/api/v1.0/startdate<br/>"
        f"/api/v1.0/startdate/enddate<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Precipitation Information"""
    
    # Date Info
    most_recent_date = session.query(func.max(measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    year_length = most_recent_date - dt.timedelta(days=365)
    
    # 12 months of precipitation data
    precipitation = session.query(measurement.date, measurement.prcp)\
        .filter(measurement.date >= year_length)\
        .all()
    
    # Convert the query results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation}

    # Return precipitation info
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Names of the stations."""
    
    # Query and return a JSON list of stations
    stations = session.query(station.name)
    station_names = [name[0] for name in stations]

    return jsonify(station_names)

@app.route("/api/v1.0/tobs")
def tobs():
    """Temperature Observations (tobs) for previous year."""
    
    # Date Info
    most_recent_date = session.query(func.max(measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    year_length = most_recent_date - dt.timedelta(days=365)
    
    # Query tobs for most active station
    most_active_station = session.query(measurement.station, func.count(measurement.station))\
        .group_by(measurement.station)\
        .order_by(func.count(measurement.station).desc())\
        .first()
    
    most_active_station_id = most_active_station[0]
    
    tobs = session.query(measurement.date, measurement.tobs)\
        .filter(measurement.station == most_active_station_id)\
        .filter(measurement.date >= year_length)\
        .all()
    
    # Format the data into dictionary
    tobs_list = [{"date": date, "temperature": temp} for date, temp in tobs]
    
    # Return list of tobs
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def temp_stats_start(start):
    """Temperature information for a specific date in YYYY-MM-DD format."""
    
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    
    # Query and calculate temperature statistics (TMIN, TAVG, TMAX) for dates greater than or equal to start date
    single_temp = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs))\
        .filter(measurement.date >= start_date)\
        .first()
    
    single_result = [tuple(single_temp) for row in single_temp]
    
    # Return list of temperature statistics
    return jsonify(single_result[0])

@app.route("/api/v1.0/<start>/<end>")
"""def temp_stats_range(start, end):
    ""Temperature information for a specific range in YYYY-MM-DD format.""
    
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')

    # Query and calculate temperature statistics (TMIN, TAVG, TMAX) for dates within the start-end range
    range_temp = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs))\
        .filter(measurement.date >= start_date)\
        .filter(measurement.date <= end_date)\
        .first()    
    
    
    range_results = []
     
    # Return list of temperature statistics
    return jsonify(range_results)

if __name__ == '__main__':
    app.run(debug=True)