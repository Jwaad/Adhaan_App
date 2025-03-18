# Written by Jwaad Hussain 2025
# TODO: 
#   HIGH PRIOIRTY----------------------
#   REMEMBER PREVIOUS SIZE AND POS
#
#   LOW PRIORITY-----------------------
#   DOWNLOAD WHOLE REST OF MONTH TO MEM
#   OPTIONS MENU FOR CUSTOMISATION
#   OTHER PRAYER CALCS
#   MOUSE OVER ICONS FOR EXTRA INFO
#   CALCULATE LAST THIRD
#   Fix strange horizontal minimizing behaviour
#   Alarms / adthaans
#   Reminder / ding ding

import sys
import datetime
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class AdhaanApp(QMainWindow):
    def __init__(self):
        """
        Initialises the Salaat Times window, setting its size and initialising its buttons.
        """
        # Init QWidgets
        super().__init__()
        
        # Check if another instance is running
        self.memory = QSharedMemory("AdthaanAppHussain")
        if self.memory.attach():
            print("Application is already running!")
            sys.exit()  # Exit if the app is already running
        
        # Init window
        self.setWindowTitle('Salaat Times')
        self.WindowSize = (300, 500) # (width, height)
        self.setGeometry(1500, 300, self.WindowSize[0], self.WindowSize[1]) # x-position, y-position, width, height
        self.WinHeightAtPreviousResize = self.WindowSize[1]
        self.setWindowIcon(QIcon("icon.png"))
        
        # Setup tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("icon.png"))  # Use a suitable icon file
        self.tray_icon.setVisible(False)
        tray_menu = QMenu()
        restore_action = QAction("Restore", self)
        restore_action.triggered.connect(self.RestoreWindowFromTray)
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.QuitAppFromTray)
        tray_menu.addAction(restore_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.setWindowFlags(self.windowFlags() | 0x00000001)  # Qt::WindowMinimizeButtonHint
        self.tray_icon.activated.connect(self.OnTrayIconActivation)
        
        # Setup widget layout
        widget = QWidget(self)
        self.setCentralWidget(widget)
        self.layout = QGridLayout()
        self.layout.setHorizontalSpacing(0)
        self.layout.setVerticalSpacing(0)
        self.layout.setContentsMargins(5, 5, 5, 5)  # Set margins to 0
        self.layout.setSpacing(0)
        widget.setLayout(self.layout)
        
        # Init program fonts
        self.DefaultFontSize = 15
        self.DefaultLargeFontSize = 30
        self.DefaultTitleFontSize = 50
        self.DefaultFont = "Verdana"

        # Get initial prayer times
        self.DefaultAPI = "http://www.londonprayertimes.com/api/times/"
        self.APIKey = "17522509-896f-49b7-80c8-975c4be643b4"
        self.GetPrayerTimes()
        
        # Populate default buttons
        self.MainPageButtons()
        
        # Initial time update
        self.UpdateCurrentTime()
        self.UpdateTilUntilNextPrayer()
        
        # Timer to update clock every second
        self.SecondTimer = QTimer(self)
        self.SecondTimer.timeout.connect(self.UpdateCurrentTime)
        self.SecondTimer.start(1000)  # 1000 ms = 1 second
    
    def OnTrayIconActivation(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.RestoreWindowFromTray()  # Restore the window if double-clicked
        elif reason == QSystemTrayIcon.MiddleClick:
            self.QuitAppFromTray()
            
    def changeEvent(self, event):
        """Override the close event to minimize to the system tray instead of quitting."""
        if event.type() == QEvent.WindowStateChange:
            if self.isMinimized():
                self.hide()  # Hide the window and keep it running in the system tray
                self.tray_icon.setVisible(True)

    def RestoreWindowFromTray(self):
        """Restore the window when clicking the 'Restore' action in the tray menu."""
        self.tray_icon.setVisible(False)
        self.show()
        self.activateWindow()

    def QuitAppFromTray(self):
        """Quit the app when clicking the 'Quit' action in the tray menu."""
        QApplication.quit()
        
    def UpdateCurrentTime(self):
        """Updates the QLabel with the current time."""
        timeNow = datetime.datetime.now()
        self.AllWidgets["CurrentTime"]["Widgets"][0].setText(timeNow.strftime("%H:%M:%S"))
        
        # Update prayer time each minute
        if timeNow.strftime("%S") == "00":
            # TODO add a backup method incase the second gets skipped (low priority)
            self.UpdateTilUntilNextPrayer()
        
    
    def UpdateTilUntilNextPrayer(self):
        """Updates the QLabel with the current time."""
        #print("TODO: UpdateTilUntilNextPrayer")
        timeNow = datetime.datetime.now()
        for prayer in self.PrayerTimes:
            prayerDatetime = datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d") + prayer["time"], "%Y-%m-%d%H:%M")
            if timeNow <= prayerDatetime:
                # self.NameOfNext = prayer["name"]
                timeTilNext = prayerDatetime - datetime.datetime.now()  # TODO should be calculated
                formattedTimeTilNext = str(timeTilNext).split(":")
                self.AllWidgets["TimeUntilNextPrayer"]["Widgets"][0].setText("Time until {}: {}h {}m".format(prayer["name"],formattedTimeTilNext[0], formattedTimeTilNext[1]))
                return
        
    def GetPrayerTimes(self):
        """
        Retrieves prayer times from API (currently hardcoded) and populates relevant instance variables. 
        """
        # Call API and get todays prayer times
        year = datetime.datetime.now().strftime("%Y")
        month = datetime.datetime.now().strftime("%m")
        day = datetime.datetime.now().strftime("%d")
        response = requests.get("http://www.londonprayertimes.com/api/times/?format=json&24hours=true&year={}&month={}&key={}".format(year,month, self.APIKey))
        apiResponse = response.json()
        todaysPrayerTimes = apiResponse["times"][datetime.datetime.now().strftime("%Y-%m-%d")]
        # print(response.status_code) # TODO handle error codes here
        
        # Get islamic midnight time
        datetimeMaghrib = datetime.datetime.strptime(year + "-" + month + "-" + day + todaysPrayerTimes["magrib"], "%Y-%m-%d%H:%M")
        datetimeFujr = datetime.datetime.strptime(year + "-" + month + "-" + day + todaysPrayerTimes["fajr"], "%Y-%m-%d%H:%M")
        midnight = (datetimeMaghrib + (datetimeFujr - datetimeMaghrib) / 2).strftime("%H:%M")
        
        #store prayer times in dict
        self.PrayerTimes = [{"name":"Fujr", "time":todaysPrayerTimes["fajr"], "font_size": self.DefaultFontSize},
                            {"name":"Sunrise", "time":todaysPrayerTimes["sunrise"], "font_size": self.DefaultFontSize},
                            {"name":"Dhuhr", "time":todaysPrayerTimes["dhuhr"], "font_size": self.DefaultFontSize},
                            {"name":"Asr", "time":todaysPrayerTimes["asr"],"font_size": self.DefaultFontSize},
                            {"name":"Maghrib", "time":todaysPrayerTimes["magrib"],"font_size": self.DefaultFontSize},
                            {"name":"Isha", "time":todaysPrayerTimes["isha"],"font_size": self.DefaultFontSize},
                            {"name":"Midnight", "time":midnight,"font_size": self.DefaultFontSize}] # TEMP. TODO: add method to get prayer times from API

    def MainPageButtons(self):
        # nRows x 5Col grid
        
        self.AllWidgets = {}
        
        smallRowSpan = 1
        normalRowSpan = 2
        normalColSpan = 1
        maxColSpan = 5
        
        standardSizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Ignored)
        self.TimeWidgets = [{"name":"CurrentDate", "default_text":datetime.datetime.now().strftime("%d/%m/%Y"), "type":QLabel, "alignment":Qt.AlignCenter,"size_policy":standardSizePolicy, "row_span":smallRowSpan, "col_span":maxColSpan, "font_size":self.DefaultFontSize},
                        {"name":"CurrentTime", "default_text":datetime.datetime.now().strftime("%H:%M:%S"), "type":QLabel, "alignment":Qt.AlignCenter,"size_policy":standardSizePolicy, "row_span":normalRowSpan, "col_span":maxColSpan, "font_size":self.DefaultLargeFontSize},
                        {"name":"TimeUntilNextPrayer", "default_text": "Time Until ?: ?h ?m", "type":QLabel, "alignment":Qt.AlignCenter,"size_policy":standardSizePolicy, "row_span":smallRowSpan, "col_span":maxColSpan, "font_size":self.DefaultFontSize}]
        
        # Populate time widgets
        rows = 1
        for widget in self.TimeWidgets:
            label = widget["type"](widget["default_text"], self)
            label.setFont(QFont(self.DefaultFont, widget["font_size"]))
            label.setSizePolicy(widget["size_policy"])
            if widget["type"] == QLabel:
                label.setAlignment(widget["alignment"])
            elif widget["type"] == QFrame:
                line.setLineWidth(widget["line_width"])
            self.layout.addWidget(label, rows, 1, widget["row_span"], widget["col_span"])
            self.AllWidgets[widget["name"]] = {"Widgets": [label], "Font": self.DefaultFont, "FontSize": widget["font_size"]}
            rows += widget["row_span"]
        
        # Add seperating line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        lineSizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        line.setSizePolicy(lineSizePolicy)
        line.setLineWidth(5)
        self.layout.addWidget(line, rows, 1, smallRowSpan, maxColSpan)
        self.AllWidgets["HLine"] = {"Widgets": [line], "Font": None, "FontSize": None, "lineWidth": 5}
        rows += smallRowSpan

        # Populate Prayer times
        for time in self.PrayerTimes:
            prayerName = QLabel(time["name"], self)
            prayerName.setFont(QFont(self.DefaultFont, self.DefaultLargeFontSize))
            prayerName.setAlignment(Qt.AlignRight)
            prayerName.setSizePolicy(standardSizePolicy)
            self.layout.addWidget(prayerName, rows, 1, normalRowSpan, 2)
            
            colon = QLabel(":", self)
            colon.setFont(QFont(self.DefaultFont, self.DefaultLargeFontSize))
            colon.setAlignment(Qt.AlignCenter)
            colon.setSizePolicy(standardSizePolicy)
            self.layout.addWidget(colon, rows, 3, normalRowSpan, 1)
            
            prayerTime = QLabel(time["time"], self)
            prayerTime.setFont(QFont(self.DefaultFont, self.DefaultLargeFontSize))
            prayerTime.setAlignment(Qt.AlignLeft)
            prayerTime.setSizePolicy(standardSizePolicy)
            self.layout.addWidget(prayerTime, rows, 4, normalRowSpan, 2)

            rows += normalRowSpan
            
            self.AllWidgets[time["name"]] = {"Widgets": [prayerName, colon, prayerTime], "Font": self.DefaultFont, "FontSize": self.DefaultLargeFontSize}
 
    def resizeEvent(self, event):

            new_size = event.size()
            stepSize = 20
            
            if abs(self.WinHeightAtPreviousResize - new_size.height()) < stepSize:
                return
            
            # Update font sizes based on height change
            self.TextScalar = new_size.height() / self.WindowSize[1] # % increase of height
            
            # Update font sizes of each widget if applicable
            for key in self.AllWidgets.keys():
                
                # Qlabels with single widget
                if len(self.AllWidgets[key]["Widgets"]) == 1:
                    widget = self.AllWidgets[key]["Widgets"][0]

                    if widget.__class__.__name__ == 'QLabel':
                        widget.setFont(QFont(self.AllWidgets[key]["Font"], int(round(self.AllWidgets[key]["FontSize"] * self.TextScalar, 0))))
                    
                    continue
                
                # Qlabels with multiple widgets
                for widget in self.AllWidgets[key]["Widgets"]:
                    if widget.__class__.__name__ == 'QLabel':
                        widget.setFont(QFont(self.AllWidgets[key]["Font"], int(round(self.AllWidgets[key]["FontSize"] * self.TextScalar, 0))))
                
            self.WinHeightAtPreviousResize = new_size.height() 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    adhaanApp = AdhaanApp()
    adhaanApp.show()
    sys.exit(app.exec_())
