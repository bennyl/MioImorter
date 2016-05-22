#%%
import zlib
import tarfile
import io

with open("backup.ab", 'r') as compressed:
    header = compressed.read(24)
    data = zlib.decompress(compressed.read())
    memfile  = io.BytesIO(data)
    with tarfile.open(fileobj=memfile) as t:
        with open("mio_db", 'w') as o:
            f = t.extractfile("apps/com.mioglobal.android.miogo/db/mio_db")
            o.write(f.read())
    
#%%
# TABLE workout
#0 id integer primary key autoincrement,
#1 icontype integer,
#2 second integer,
#3 minute integer,
#4 hour integer,
#5 day integer,
#6 month integer,
#7 year integer,
#8 exerciseSecond integer,
#9 exerciseMinute integer,
#10 exerciseHour integer,
#11 step integer,
#12 dist integer,
#13 calorie integer,
#14 maxSpeed integer,
#15 timeInZone integer,
#16 timeInZone1 integer,
#17 timeInZone2 integer,
#18 timeInZone3 integer,
#19 timeInZone4 integer,
#20 timeInZone5 integer,
#21 aHR integer,
#22 avghrs integer,
#23 maxhrs integer,
#24 avgspeeds integer,
#25 maxspeeds integer,
#26 avgpaces integer,
#27 maxpaces integer, 
#28 hrArray text, 
#29 limit1 integer, 
#30 limit2 integer, 
#31 limit3 integer, 
#32 limit4 integer, 
#33 limit5 integer, 
#34 workoutTypeEx integer, 
#35 mapsTrackData text, 
#36 elevation real, 
#37 otherActivity varchar(255));

import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
import sqlite3
import json
con=sqlite3.connect("mio_db")
cur=con.execute("SELECT * FROM workout")

header = '''
<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<TrainingCenterDatabase xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation
="http://www.garmin.com/xmlschemas/ActivityExtension/v2 http://www.garmin.com/xmlschemas/ActivityExtensionv2.xsd http://www.garmin.com/xmlschemas/TrainingCenterDat
abase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd">
'''
footer = '''</TrainingCenterDatabase>'''

Activities = Element('Activities')

for item in cur.fetchall():
    act_type = "Other"
    if item[1] == 1 or item[1] == 14:
        act_type = "Running"
    if item[1] == 2 or item[1] == 4 or item[1] == 12:
        act_type = "Biking"

    Activity = SubElement(Activities, "Activity", {'Sport':act_type})
    
    stime = datetime.datetime(item[7], item[6], item[5], item[4], item[3], item[2])
    n = SubElement(Activity, "Id")
    n.text = stime.strftime("%Y-%m-%dT%H:%M:%SZ")
    lap = SubElement(Activity, "Lap", {'StartTime':stime.strftime("%Y-%m-%dT%H:%M:%SZ")})
    
    secs = int(item[8]) + 60*(int(item[9]) + 60*int(item[10]))
    n = SubElement(lap, "TotalTimeSeconds")
    n.text = str(secs)
    n = SubElement(lap, "DistanceMeters")
    n.text = str(item[12])
    n = SubElement(lap, "MaximumSpeed")
    n.text = str(item[14])
    n = SubElement(lap, "Calories")
    n.text = str(item[13])
    n = SubElement(lap, "Intensity")
    n.text = "Active"
    n = SubElement(lap, "TriggerMethod")
    n.text = "Manual"

    hr = SubElement(lap, "AverageHeartRateBpm", {'xsi:type':"HeartRateInBeatsPerMinute_t"})
    n = SubElement(hr, "Value")
    n.text = str(item[22])
    
    mhr = SubElement(lap, "MaximumHeartRateBpm", {'xsi:type':"HeartRateInBeatsPerMinute_t"})
    n = SubElement(mhr, "Value")
    n.text = str(item[23])
        
    hrpoints = json.loads(item[28])        
    mapsects = json.loads(item[35])    

    countp = 0
    for s in mapsects:
        countp = countp + len(s['latLng'])            
    
    if countp > 0:
        track = SubElement(lap, "Track")
        hrr = float(countp) / float(len(hrpoints)+1)
        curp = 0
        for s in mapsects:
            for p in s['latLng']:
                trackp = SubElement(track, "Trackpoint")
                ptime = stime + datetime.timedelta(seconds=curp * float(secs) / float(countp))
                n = SubElement(trackp, "Time")
                n.text = ptime.strftime("%Y-%m-%dT%H:%M:%SZ")
                #SubElement(trackp, "AltitudeMeters", {'text':str(0)})
                
                sensor = SubElement(trackp, "SensorState")            
                if len(hrpoints) > 0:
                    curhr = int(curp / hrr)
                    n = SubElement(trackp, "HeartRateBpm", {'xsi:type':"HeartRateInBeatsPerMinute_t"})
                    n = SubElement(n, "Value")
                    n.text = str(hrpoints[curhr])
                    sensor.text = 'Present'
                else:
                    sensor.text = 'Absent'
                    
                pos = SubElement(trackp, "Position")
                n = SubElement(pos, "LatitudeDegrees")
                n.text = str(p['latitude'])
                n = SubElement(pos, "LongitudeDegrees")
                n.text = str(p['longitude'])
                curp = curp + 1
    else:
        track = SubElement(lap, "Track")
        for curp in range(len(hrpoints)):
            trackp = SubElement(track, "Trackpoint")
            ptime = stime + datetime.timedelta(seconds=curp * float(secs) / float(len(hrpoints)))
            n = SubElement(trackp, "Time")
            n.text = ptime.strftime("%Y-%m-%dT%H:%M:%SZ")
            #SubElement(trackp, "AltitudeMeters", {'text':str(0)})
            
            sensor = SubElement(trackp, "SensorState")            
            n = SubElement(trackp, "HeartRateBpm", {'xsi:type':"HeartRateInBeatsPerMinute_t"})
            n = SubElement(n, "Value")
            n.text = str(hrpoints[curp])
            sensor.text = 'Present'
                
    print("Run: " + str(item[0]) + " on " + str(stime) + ": Seconds " + str(secs) + " Meters " + str(item[12]))
    
with open("mio_db.tcx", 'w') as tcx:
    tcx.write(header)
    tcx.write(tostring(Activities, 'utf-8'))
    tcx.write(footer)
    
