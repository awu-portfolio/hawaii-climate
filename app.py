# Import the dependencies

from flask import Flask, jsonify
from sqlalchemy import create_engine, desc, asc, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt

#################################################
# Database Setup
#################################################

# reflect an existing database into a new model

path = "data/hawaii.sqlite"
engine = create_engine(f"sqlite:///{path}")

Base = automap_base()

# Reflect the tables

Base.prepare(autoload_with=engine)

# Save references to each table

Station = Base.classes.station
Measurement = Base.classes.measurement

# Create session (link) from Python to the DB

session = Session(bind=engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def homepage():
    return """
        All available routes:<br>
        Precipitation Analysis: http://127.0.0.1:5000/api/v1.0/precipitation<br>
        List of Stations: http://127.0.0.1:5000/api/v1.0/stations<br>
        Temperature Observations for Most Active Station: http://127.0.0.1:5000/api/v1.0/tobs<br>
        Temperature Data for Specified Start Date: http://127.0.0.1:5000/api/v1.0/YYYY-MM-DD<br>
        Temperature Data for Specified Start and End Dates: http://127.0.0.1:5000/api/v1.0/YYYY-MM-DD/YYYY-MM-DD<end><br>
    """

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    recent_date_row = session.query(Measurement.date).order_by(desc(Measurement.date)).first()
    recent_date = dt.datetime.strptime(recent_date_row[0], '%Y-%m-%d')

    past_year = recent_date - dt.timedelta(days=365)

    past_year_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= past_year).all()

    data = {}
    for r in past_year_data:
        if r.date not in data:
            data[r.date] = []
        data[r.date].append(r.prcp)

    return jsonify(data)

@app.route("/api/v1.0/stations")
def stations():

    stations = session.query(Measurement.station).\
        group_by(Measurement.station).all()

    station_data = [r.station for r in stations]

    return jsonify(station_data)

@app.route("/api/v1.0/tobs")
def tobs():

    recent_date_row = session.query(Measurement.date).order_by(desc(Measurement.date)).first()
    recent_date = dt.datetime.strptime(recent_date_row[0], '%Y-%m-%d')

    past_year = recent_date - dt.timedelta(days=365)

    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(desc(func.count(Measurement.station))).all()
    most_active = active_stations[0]
    active_station = most_active[0]

    temp_data_query = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == active_station).\
        filter(Measurement.date >= past_year).all()

    temp_data = {
        r.date: r.tobs for r in temp_data_query
    }

    return jsonify(temp_data)
    

@app.route("/api/v1.0/<start>")
def specified_start(start):

    try:
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")

        recent_date_row = session.query(Measurement.date).order_by(desc(Measurement.date)).first()
        recent_date = dt.datetime.strptime(recent_date_row[0], '%Y-%m-%d')

        tmin = session.query(func.min(Measurement.tobs)).\
            filter(Measurement.date >= start_date).scalar()

        tmax = session.query(func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).scalar()

        tavg = session.query(func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start_date).scalar()

        stats = {
            "Min Temp": tmin,
            "Max Temp": tmax,
            "Avg Temp": tavg
        }

        return jsonify(stats)
        
    except:
        return "Error: Invalid date format. Use YYYY-MM-DD."

@app.route("/api/v1.0/<start>/<end>")
def specified_dates(start, end):

    try:
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
        end_date = dt.datetime.strptime(end, "%Y-%m-%d")

        tmin = session.query(func.min(Measurement.tobs)).\
            filter(Measurement.date >= start_date).\
            filter(Measurement.date <= end_date).scalar()

        tmax = session.query(func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).\
            filter(Measurement.date <= end_date).scalar()

        tavg = session.query(func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start_date).\
            filter(Measurement.date <=end_date).scalar()

        stats = {
            "Min Temp": tmin,
            "Max Temp": tmax,
            "Avg Temp": tavg
        }

        return jsonify(stats)
        
    except:
        return "Error: Invalid date format. Use YYYY-MM-DD/YYYY-MM-DD."

if __name__ == "__main__":
    app.run(debug=True)



























