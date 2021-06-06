
from astropy.time import Time
from flask import Flask, render_template, redirect, request, json
from flask.helpers import url_for
from spacetrack import SpaceTrackClient
from astropy.time import TimezoneInfo  # Specifies a timezone
import astropy.units as u


app = Flask(__name__)



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
    return "search"
"""
    data = []
    
    search for satellite by ID
    if request.method == "POST":
        if request.form.get("search"):
            id = request.form["id"]
            data = TLE(id)
        if request.form.get("date"):
            date = request.form["date"]  

    return render_template("search.html", data = data)

"""
@app.route('/calculate',methods = ['GET', 'POST'])
def calculate():
    return "calculate"
"""
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "tle.json")
    data = json.load(open(json_url))
    sat = c.satData(data)
    output = {}
    if request.method == "POST":
        date = request.form["date"]
        date = Time(date)
        timezone = request.form["timezone"]
        print(type(timezone))
        print(timezone)
        timezone = -int(timezone)
        epoch = c.EpochToDate(sat.epoch)
        M = format(float(c.calMean(epoch, date, sat.motion, sat.M, timezone)), '.3f')
        E = format(float(c.solveE(M, sat.e)), '.3f')
        v = format(float(c.calTrue(E, sat.e)), '.3f')
        t = date - epoch
        t = t.sec
        position = c.toRA(sat.i, sat.peri, v, sat.RAAN)
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
        with open("static/celes.txt", "w") as json_file:
            data = json.dump(celes_obj, json_file, indent=4)
        
        
    return render_template('calculate.html', data=data, output = output)
"""



if __name__ == "__main__":
    app.run(debug=True)


