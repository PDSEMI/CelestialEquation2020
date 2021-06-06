from astropy.coordinates import calculation
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from astropy.time import Time
from flask import Flask, render_template, redirect, request, json
from flask.helpers import url_for
from spacetrack import SpaceTrackClient
from astropy.time import TimezoneInfo  # Specifies a timezone
import astropy.units as u
import calculation as c


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

def TLE(id):
    username = 'natthaphat_ph@kkumail.com'
    password = 'PDSEMI1215natthaphat'
    st = SpaceTrackClient(username, password)
    data = st.tle_latest(norad_cat_id=[id], ordinal=1, format='3le')    
    tle_data = data[1:-1]  
    #print("tle data : ", tle_data)
    tle_data_strip = tle_data.strip()
    tle_data_splitlines = tle_data_strip.splitlines()
    line1 = tle_data_splitlines
    line2 = tle_data_splitlines[1].split()
    line3 = tle_data_splitlines[2].split()
    if line2[-6] == line2[3]:
        date = line2[3]
    else:
        date = line2[3]+line2[4]
    tle_obj = {
        "name":line1[0],
        "desig":line2[2],
        "beta":line2[-3],
        "second":line2[-4],
        "first":line2[-5],
        "epoch":date,
        "catalog":line3[1],
        "i":line3[2],
        "RAAN":line3[3],
        "e":"0." + line3[4],
        "peri":line3[5],
        "M":line3[6],
        "motion":line3[7],
    }
    
    #print(tle_obj)
    """
    with open("tle.json", "w") as json_file:
        data = json.dump(tle_obj, json_file, indent=4)
    """
    return tle_obj

class Satellite(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20))
    desig = db.Column(db.String(20))
    beta = db.Column(db.String(20))
    second = db.Column(db.String(20))
    first = db.Column(db.String(20))
    epoch = db.Column(db.String(20))
    catalog = db.Column(db.String(20))
    i = db.Column(db.String(20))
    RAAN = db.Column(db.String(20))
    e = db.Column(db.String(20))
    peri = db.Column(db.String(20))
    M = db.Column(db.String(20))
    motion = db.Column(db.String(20))

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/intro')
def intro():
    return render_template("introduction.html")

@app.route('/ack')
def ack():
    return render_template("ack.html")

@app.route('/method')
def method():
    return render_template("method.html")


@app.route('/search',methods = ['GET', 'POST'])
def search():
    #return "search"
    data = []
    if request.method == "POST":
        if request.form.get("search"):
            id = request.form["id"]
            data = TLE(id)

            obj = Satellite.query.get(1)
            obj.name = data["name"]
            obj.desig = data["desig"]
            obj.beta = data["beta"]
            obj.second = data["second"]
            obj.first = data["first"]
            obj.epoch = data["epoch"]
            obj.catalog = data["catalog"]
            obj.i = data["i"]
            obj.RAAN = data["RAAN"]
            obj.e = data["e"]
            obj.peri = data["peri"]
            obj.M = data["M"]
            obj.motion = data["motion"]
            
            
            db.session.commit()

    return render_template("search.html", data = data)


@app.route('/calculate',methods = ['GET', 'POST'])
def calculate():
    data = Satellite.query.get(1)
    output = {}
    if request.method == "POST":
        date = request.form["date"]
        date = Time(date)
        timezone = request.form["timezone"]
        print(type(timezone))
        print(timezone)
        timezone = -int(timezone)
        epoch = c.EpochToDate(data.epoch)
        M = format(float(c.calMean(epoch, date, data.motion, data.M, timezone)), '.3f')
        E = format(float(c.solveE(M, data.e)), '.3f')
        v = format(float(c.calTrue(E, data.e)), '.3f')
        t = date - epoch
        t = t.sec
        position = c.toRA(data.i, data.peri, v, data.RAAN)
        RA = format(float(position[0]), '.3f')
        dec = format(float(position[1]), '.3f')
    
        output = {
            "epoch":epoch,
            "date":date,
            "E" : E,
            "M" : M,
            "v" : v,
            "deltaT" : t,
            "zone":timezone,
            "RA":RA,
            "dec":dec
        }

        celes_obj = {
            "RA":RA,
            "dec":dec
        }
        """
        with open("static/celes.txt", "w") as json_file:
            data = json.dump(celes_obj, json_file, indent=4)
        """
        
    return render_template('calculate.html', data=data, output = output)




if __name__ == "__main__":
    app.run(debug=True)


