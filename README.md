Exporting data from Mio to to Training Center Database XML (TCX) file format.

First, get the data from the phone. Debug mode needs to be enabled and Android SDK is needed as well.

adb backup --noapk com.mioglobal.android.miogo

This generates a file called backup.ad
The python script opens the file, extracts mio_db and writes the tcx file to mio_db.tcs.
