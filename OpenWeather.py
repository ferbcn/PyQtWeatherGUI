#!/usr/bin/python3

"""
Weather GUI

Requirements:
PyQt5
requests

Author: Fernando Garcia Winterling
Last edited: Mai 2018

TODO: improvement ideas
- add edit/save of location list: json read/write
- add graphical view of temperature (+hum. +press.)
- add toolbox for location info: maybe scrapp some data from wikipedia

"""
import sys
from datetime import datetime
import time
import os
import requests

from PyQt5 import QtGui
from PyQt5.QtWidgets import (QApplication, qApp, QMainWindow)
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap

from urllib.parse import urlencode

#from PyQt5.uic import loadUi #needed to load the .ui file directly
from OpenWeatherUI import Ui_MainWindow

#custom wrapper to retrieve water temperatures in Zurich
from WaterTempAPI import WaterTempAPI

# load API key from environment variable
#OPENWEATHERMAP_API_KEY = os.environ.get('OPENWEATHERMAP_API_KEY')
# hard coded city list
#LOCATIONS = ['Auckland', 'Christchurch', 'Zurich', 'Barcelona', 'Trier', 'Benicassim', 'Hamburg', 'Dusseldorf', 'San Jose, CR', 'San Francisco', 'Sydney', 'Hong Kong']

# load API key and cities from file
from config import LOCATIONS, OPENWEATHERMAP_API_KEY

# helper function for time (currently not used)
def from_ts_to_time_of_day(ts):
    dt = datetime.fromtimestamp(ts)
    return dt.strftime("%I%p").lstrip("0")


# Main App
class App(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(App, self).__init__()
        self.setupUi(self)
        self.show()
        self.initUI()


    def initUI(self):

        self.locNum = 0

        # get screen size and set app size
        screen_resolution = app.desktop().screenGeometry()
        self.screenW, self.screenH = screen_resolution.width(), screen_resolution.height()

        # set position
        self.setGeometry(self.screenW * 0.9, 0, self.screenW * 0.1, self.screenH * 0.5)

        self.setWindowTitle("Open Weather GUI")
        #self.move()

        #connect the buttons and comboBox to functions
        self.exitButton.clicked.connect(qApp.quit)
        self.updateButton.clicked.connect(self.runUpdateWeather)
        self.comboBox.activated[str].connect(self.selectLoc)

        #add items to drop down menu
        for location in LOCATIONS:
            self.comboBox.addItem(location)

        timer0 = QTimer(self)
        timer0.timeout.connect(self.showTime)
        timer0.start(100)

        timer1 = QTimer(self)
        timer1.timeout.connect(self.runUpdateWeather)
        timer1.start(60000)

        #initial update
        self.updateWeather(LOCATIONS[0])


    def selectLoc(self, loc):
        self.location = loc
        i = 0
        for l in LOCATIONS:
            if l == loc:
                self.locNum = i
                break
            else:
                i += 1
        self.updateWeather(loc)


    def runUpdateWeather(self):
        self.locNum += 1
        if self.locNum > len(LOCATIONS) - 1:  # and reset counter when > len-1
            self.locNum = 0
        self.location
        self.updateWeather(loc=LOCATIONS[self.locNum])


    def updateWeather(self, loc):

        #read current location from array and then increment index counter "locNum"
        #update location info

        self.location = loc
        print('### ' + self.location + ' ###')
        self.label.setText("<h1>" + self.location + "</h1>")
        self.comboBox.setCurrentText(self.location)

        try:
            params = dict(
                q=self.location,
                appid=OPENWEATHERMAP_API_KEY
            )

            url = 'http://api.openweathermap.org/data/2.5/weather?%s&units=metric' % urlencode(params)
            r = requests.get(url)
            self.weather = r.json()

            # Check if we had a failure (the forecast will fail in the same way).
            if self.weather['cod'] != 200:
                raise Exception(self.weather['message'])

            url = 'http://api.openweathermap.org/data/2.5/forecast?%s&units=metric' % urlencode(params)
            r = requests.get(url)
            self.forecast = r.json()
            self.updateGUI()

        except Exception as e:
            print(str(e))


    def updateGUI(self):

        self.tempNow = self.weather['main']['temp']
        self.humNow = self.weather['main']['humidity']
        self.pressNow = self.weather['main']['pressure']

        self.fcstTemps = []

        fcstList = self.forecast["list"]

        for fcst in fcstList:
            d = str(fcst['weather'])
            d1 = d[d.find('description')+15:len(d)]
            d2 = d1[0:d1.find('\',')]
            self.fcstTemps.append(fcst['main']['temp'])
            text = fcst['dt_txt'] + "\n" + str(fcst['main']['temp']) + "°C - " + d2 + "\n"
            #print(text)

        self.tempMin = min(self.fcstTemps[0:7])
        self.tempMax = max(self.fcstTemps[0:7])

        self.showLCDData()


        # set preview icons and temperatures
        for n, fcast in enumerate(self.forecast['list'][:24], 8):
            self.set_weather_icon(getattr(self, 'forecastIcon%d' % int(n / 8) + "_2"), fcast['weather'])

        self.forecastTemp1.setText("%.1f" % self.fcstTemps[1] + "°")
        self.forecastTemp2.setText("%.1f" % self.fcstTemps[2] + "°")
        self.forecastTemp3.setText("%.1f" % self.fcstTemps[3] + "°")
        self.forecastTemp4.setText("%.1f" % self.fcstTemps[4] + "°")
        self.forecastTemp5.setText("%.1f" % self.fcstTemps[5] + "°")

        #set current weather icon and label
        self.set_weather_icon(self.weatherIcon, self.weather['weather'])

        self.weatherLabel.setText("%s (%s)" % (self.weather['weather'][0]['main'], self.weather['weather'][0]['description']))

        # set 3-day forecast icons and temperatures
        for n, fcast in enumerate(self.forecast['list'][:5], 1):
            #print(fcast['weather'])
            self.set_weather_icon(getattr(self, 'forecastIcon%d' % n), fcast['weather'])

        self.forecastTemp1_2.setText("%.1f" % self.fcstTemps[0] + "°")
        self.forecastTemp2_2.setText("%.1f" % self.fcstTemps[8] + "°")
        self.forecastTemp3_2.setText("%.1f" % self.fcstTemps[16] + "°")

        #if Zurich set water temperature and icon
        if self.location == 'Zurich':
            self.waterIcon.setPixmap(QPixmap(os.path.join('images', "%s.png" % "water_mini")))
            titel, tempStr = WaterTempAPI.getTemp(self, 0)
            self.waterTemp.setText(tempStr)
            self.waterTemp.setToolTip('Wassertemperatur ' + titel)
        else:
            self.waterIcon.clear()
            self.waterTemp.clear()


    def set_weather_icon(self, label, weather):
        label.setPixmap(QPixmap(os.path.join('images', "%s.png" % weather[0]['icon'])))


    def showLCDData(self):

        # set color of lcd1
        palette = self.lcd1.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(250, 150, 50))  # foreground color
        self.lcd1.setPalette(palette)  # set the palette
        tempStr = "%.1f" % self.tempNow + " 'C"
        humStr = str(self.humNow) + "'o"
        pressStr = str(int(self.pressNow))+ " "
        tempMinStr = "%.1f" % self.tempMin + "'C"
        tempMaxStr = "%.1f" % self.tempMax + "'C"

        self.lcd1.display(tempStr)
        self.lcd2.display(tempMinStr)
        self.lcd3.display(tempMaxStr)
        self.lcd4.display(humStr)
        self.lcd5.display(pressStr)


    def showTime(self):

        # LCD0 "Time"
        timeNow = datetime.now()
        timeNow = time.mktime(timeNow.timetuple())

        #set color of lcd0
        palette = self.lcd0.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(250, 150, 50))         # foreground color
        self.lcd0.setPalette(palette)           # set the palette

        value = datetime.fromtimestamp(timeNow)
        timeStr = value.strftime('%Y-%m-%d %H:%M:%S')
        #timeStr = value.strftime('%H:%M:%S')
        self.lcd0.display(timeStr)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    myApp = App()
    sys.exit(app.exec_())


