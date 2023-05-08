import numpy as np
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from datetime import datetime, timedelta

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine, reflect=True)


# View all of the classes that automap found
#Base.classes.keys()

# Save references to each table
Measurementr = Base.classes.measurement
Stationr = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """Here is a List of all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>/<end>"
        f"<br/>"
        f"<br/>"
        f"<br/>"
        f"<br/>"
        f"<br/>"
        f"User guide: <br/>"
        f"For latest year's precipitation use precipitation site:<br/> "
        f"For details on all Weather Stations use stations site:<br/>"
        f"For Temperature Observations of Most active Station over its last year use tobs site:<br/>"
        f"For Min, Max and Avg Temperatures use /api/v1.0// site, supplying a start date or between two dates<br/>"
        f"If you give just a start_date with format /YYYY-MM-DD an example is /api/v1.0/2014-01-01<br/>"
        f"and if an end date is also to be used also add end_date as /YYYY-MM-DD<br/>"
        f"resulting in for example /api/v1.0/2014-01-01/2014-05-31 <br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Design a query to retrieve the last 12 months of precipitation data and plot the results. 
    max_date_query = session.query(func.max(Measurementr.date)).scalar()
    max_date = datetime.strptime(max_date_query, '%Y-%m-%d').date()
    # query to get the data within the date range

    results = session.query(Measurementr.date, Measurementr.prcp).\
    filter(Measurementr.date >= max_date - timedelta(days=365)).\
    order_by(Measurementr.date).all()

    session.close()
    all_precipitation = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        all_precipitation.append(precip_dict)

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
  

    results = session.query(Stationr.station, Stationr.name, Stationr.latitude, Stationr.longitude, Stationr.elevation).all()

    session.close()
    all_stations = []
    for station, name, latitude, longitude, elevation  in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
  

    mostactive_max_date = session.query(func.max(Measurementr.date)).\
    filter(Measurementr.station == 'USC00519281').scalar()

    # convert string to datetime object
    mostactive_max_date = datetime.strptime(mostactive_max_date, '%Y-%m-%d')
    # query to get the data within the date range
    query = session.query(Measurementr.station,Measurementr.date, Measurementr.tobs).\
                filter(Measurementr.date >= mostactive_max_date - timedelta(days=365)).\
                filter(Measurementr.station == 'USC00519281')

    results = query.all()
    
    session.close()
    popstationtob = []
    for station, date, tobs  in results:
        popstationtob_dict = {}
        popstationtob_dict["station"] = station
        popstationtob_dict["date"] = date
        popstationtob_dict["tobs"] = tobs
        popstationtob.append(popstationtob_dict)

    return jsonify(popstationtob)


@app.route("/api/v1.0/<start>")
def start_only(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query to get the maximum date if user does not give end_date


    end = session.query(func.max(Measurementr.date)).scalar() # Get the max date as a string

# Query to get the temperature statistics within the specified date range
    actv_temp_query = session.query(func.min(Measurementr.tobs), func.avg(Measurementr.tobs), func.max(Measurementr.tobs)).\
            filter(Measurementr.date >= start).\
            filter(Measurementr.date <= end)

    actv_temp_results = actv_temp_query.all()
    session.close()

    # extract the values from the query results
    actv_min_tobs = actv_temp_results[0][0]
    actv_avg_tobs = actv_temp_results[0][1]
    actv_max_tobs = actv_temp_results[0][2]

    output = f"The temperature statistics for the date range {start} to {end} are:<br/>" \
    f"Minimum temperature: {actv_min_tobs}<br/>" \
    f"Average temperature: {actv_avg_tobs}<br/>" \
    f"Maximum temperature: {actv_max_tobs}<br/>"

    return output

###################
@app.route("/api/v1.0/<start>/<end>")
def start_and_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query to get the maximum date if user does not give end_date

    end = dt.datetime.strptime(end, '%Y-%m-%d').date() # Convert end string to a date object

# Query to get the temperature statistics within the specified date range
    actv_temp_query = session.query(func.min(Measurementr.tobs), func.avg(Measurementr.tobs), func.max(Measurementr.tobs)).\
            filter(Measurementr.date >= start).\
            filter(Measurementr.date <= end)

    actv_temp_results = actv_temp_query.all()
    session.close()

    # extract the values from the query results
    actv_min_tobs = actv_temp_results[0][0]
    actv_avg_tobs = actv_temp_results[0][1]
    actv_max_tobs = actv_temp_results[0][2]

    output = f"The temperature statistics for the date range {start} to {end} are:<br/>" \
    f"Minimum temperature: {actv_min_tobs}<br/>" \
    f"Average temperature: {actv_avg_tobs}<br/>" \
    f"Maximum temperature: {actv_max_tobs}<br/>"

    return output



if __name__ == '__main__':
    app.run(debug=True)