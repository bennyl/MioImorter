Exporting data from Mio Go Andoid app to the Training Center Database XML (TCX) file format.
It was tested with version 2.6.2 and the data could be imported in Strava including GPS tracks and heartrate.

First, get the data from the phone. Debug mode needs to be enabled and Android SDK is needed as well.

adb backup --noapk com.mioglobal.android.miogo

This generates a file called backup.ad
The python script opens the file, extracts mio_db and writes the tcx file to mio_db.tcs.
