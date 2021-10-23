from flask import Flask, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from dataclasses import dataclass

import datetime as dt

from sqlalchemy.sql.functions import count, user
#Database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurements = Base.classes.measurement
stations = Base.classes.station

#Flask setup 
app = Flask(__name__)
db = SQLAlchemy(app)
#Home page.

#List all routes that are available.
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome! Find Available Routes below:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/daterange/<start>/<end>"
    )
#Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    precipitation = session.query(measurements.date, measurements.prcp).all()
    session.close()
    precip_json = []
    for date, prcp in precipitation: 
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["precipitation"] = prcp
        precip_json.append(precip_dict)
  #Return the JSON representation of your dictionary.
    return jsonify(precip_json)

@dataclass
class station(db.Model):
  station_list: str
  station_id : int
  station_id = db.Column(db.Integer, primary_key=True, auto_increment=True)
  station_list = db.Column(db.String(200), unique=True)

@app.route("/api/v1.0/stations")
#Return a JSON list of stations from the dataset.
def list_of_stations(): 
  session = Session(engine)
  stations = session.query(measurements.station).distinct()
  session.close()
  station_list = []
  for station in stations: 
        dict_station = {}
        dict_station["station"] = station
        station_list.append(dict_station)
    #Return a JSON list of stations from the dataset.
  station_list = str(station_list)
  return jsonify(station_list)  

@app.route("/api/v1.0/tobs")
def tobs():
 # Return a JSON list of temperature observations (TOBS) for the previous year
    date = dt.datetime(2016, 8, 23)
    session = Session(engine)
    temperature = session.query(measurements.tobs,
                        measurements.date).\
                        filter(measurements.date > date).all()
    session.close()
    temp_json = []
    for temp, date in temperature: 
        temp_dict = {}
        temp_dict["temperature"] = temp
        temp_dict["date"] = date
        temp_json.append(temp_dict)
  #Return the JSON representation of your dictionary.
    return jsonify(temp_json)

@app.route("/api/v1.0/daterange/<start>/<end>")   
def startend():
    date = dt.datetime()
    session = Session(engine)
    startend = session.query(measurements.tobs,
                        measurements.date, measurements.prcp)
    session.close()
    date_dictionary = []
    for date in startend:
        start_date = startend["date"].replace(" ", "")
        # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
        # When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
        end_date = startend["date"].replace(" ", "").default(dt.datetime(2017, 8, 23))
        
        startend_min = session.query(measurements.tobs,
                        measurements.date, measurements.prcp, func.min(measurements.tobs,
                        measurements.date, measurements.prcp)).filter(measurements.date > start_date, measurements.date < end_date).all()
        startend_max = session.query(measurements.tobs,
                        measurements.date, measurements.prcp, func.max(measurements.tobs,
                        measurements.date, measurements.prcp)).filter(measurements.date > start_date, measurements.date < end_date).all()
        startend_avg = session.query(measurements.tobs,
                        measurements.date, measurements.prcp, func.avg(measurements.tobs,
                        measurements.date, measurements.prcp)).filter(measurements.date > start_date, measurements.date < end_date).all()
        
        if start_date == date and end_date == date:
            date_dictionary.append([startend_min, startend_max, startend_avg])
            return jsonify(date_dictionary)
        else:
            return jsonify({"error": "date range is invalid."}), 404
  # When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
   # return jsonify(sum_stats)
if __name__ == "__main__":
    app.run(debug=True)