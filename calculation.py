import numpy as np
import sympy as sy
import math
from astropy.time import Time
import datetime


def toRad(theta):
    #Change theta in degree to radian
    return theta * math.pi / 180


def toDeg(theta):
    #Change theta in radian to degree
    return theta *180 / math.pi


def solveE(M,e):
    """
    Numerically solve for Eccentric anomaly (E)
    Input: Mean anomaly (M), Eccentricity (e)
    """ 
    E = sy.symbols('E')
    e = float(e)
    M = float(M)
    M = toRad(M)
    F = E-e*sy.sin(E)-M
    Fderivative = F.diff(E)
    En = M
    for i in range(10):
        En = En-np.float(F.evalf(subs = {E:En}))/np.float(Fderivative.evalf(subs = {E:En}))
        #print(f'The {i+1} iteration xn is {En:.10} and f(xn) is {np.float(F.evalf(subs= {E:En})):.2}')
    
    En = toDeg(En) 
    En = str(En)
    return En

def isLeapyear(yyyy):
    if yyyy%4 == 0 and yyyy%100 != 0 and yyyy%400 != 0:
        return True
    elif yyyy%4 != 0:
        return False
    elif yyyy%4 == 0 and yyyy%100 == 0 and yyyy%400 != 0:
        return False
    elif yyyy%4 == 0 and yyyy%100 == 0 and yyyy%400 == 0:
        return True


def toEpoch(yyyy, mm, dd, time_sec):
    Epoch = ''
    day = 0
    for i in range(1,13):
        if i == mm:
            break
        if i in [1,3,5,7,8,10,12]:
            day = day + 31
        elif i in [6,9,11]:
            day = day + 30
        elif i in [2]: 
            if isLeapyear(yyyy):
                day = day + 29
            else:
                day = day +28
    day = day + dd
    if day < 100:
        day = '0' + str(day)
    if yyyy > 2000:
        yyyy = yyyy - 2000
    time_frac = time_sec
    Epoch = str(yyyy)+str(day)+str(time_frac)[1:]
    return Epoch

def fracTime(hr,minute,sec):
    time = 0
    time = time + float(hr) * 60 *60 
    time = time + float(minute) * 60
    time = time + float(sec)
    time = time/(24*60*60)
    return float(time)

def calMean(last_Epoch, next_Epoch, motion, M, zone):
    """
    Use Astropy Time to find Time delta
    Input : last_Epoch, next_Epoch must be astropy Time 
    Output : Mean anomaly (M) in degree
    """

    t = next_Epoch-last_Epoch
    t = t.sec - float(zone)*3600
    M = (float(M) + (float(motion) * t * 360)/(24*60*60)) % 360
    M = str(M)
    return M

def calTrue(E,e):
    """
    Input : eccentricity (e), Eccentric anomaly (E) in degree
    Output : True anomaly (v) in degree
    """
    E = float(E)
    E = toRad(E)
    e = float(e)
    tan_v_2 = math.sqrt((1+e)/(1-e)) * math.tan(E/2)
    v = 2 * math.atan(tan_v_2)
    v = toDeg(v)
    v = str(v)
    return v

def toRA(i, peri, v, RAAN):
    """
    Compute satellite postion in celestial coordinate (Declination, Right Ascension)
    Input : inclination (i), argument of perigee (peri), true anomaly(v), right ascension of ascending node (RAAN)
    Output : [Ra,dec] in degree
    """
    i = float(i)
    peri = float(peri)
    v = float(v)
    RAAN = float(RAAN)
    i = toRad(i)
    alpha = v + peri
    alpha = toRad(alpha)
    sin_delta = math.sin(i) * math.sin(alpha)
    delta = math.asin(sin_delta)
    
    cos_RA = math.cos(alpha)/math.cos(delta)
    tan_RA = (math.cos(delta)**2 - math.cos(alpha)**2)/(math.cos(alpha)*math.sin(alpha)*math.cos(i))

    #cos_RA = 1/2
    #tan_RA = -math.sqrt(3)
    if cos_RA > 0 and tan_RA > 0:
        RA = math.acos(cos_RA)
    elif cos_RA < 0 and tan_RA < 0:
        RA = math.acos(cos_RA)
    elif cos_RA < 0 and tan_RA > 0:
        RA = 2*math.pi - math.acos(cos_RA) 
    elif cos_RA > 0 and tan_RA < 0:
        RA = 2*math.pi - math.acos(cos_RA)
    
    dec = toDeg(delta)
    RA = (toDeg(RA) + RAAN)%360
    dec = str(dec)
    RA = str(RA)
    return [RA, dec]



def timeZone(longt):
    for i in range(0,181,15):
        if float(longt) > i - 7.5 and float(longt) < i +7.5:
            zone = int(i/15)
            return zone
        
def calUTC(hr,minute,sec,timezone):
    UTC_hr = int(hr) - int(timeZone)
    return [UTC_hr, minute, sec]

def EpochToDate(epoch):
    """
    Change TLE Epoch to Astropy Time
    """
    now = datetime.datetime.now()
    year_now = int(str(now.year)[2:])
    if int(epoch[0:2]) > year_now :
        year = '19' + epoch[0:2]
    else:
        year = '20' + epoch[0:2]
    
    JD_year = year +'-01-01'
    d = Time(JD_year)
    date = d + float(epoch[2:])-1
    return date    

class satData:
    """
    Take dictionary to initailize the satellite data class
    """
    def __init__(self, data):
        self.name = data["name"] 
        self.desig = data["desig"] 
        self.beta = data["beta"] 
        self.second = data["second"] 
        self.first = data["first"] 
        self.epoch = data["epoch"] 
        self.catalog = data["catalog"] 
        self.i = data["i"] 
        self.RAAN = data["RAAN"] 
        self.e = data["e"] 
        self.peri = data["peri"] 
        self.M = data["M"] 
        self.motion = data["motion"] 
        


