import sys
import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class AdhaanApp(QMainWindow):
    def __init__(self):
        """
        Initialises the Salaat Times window, setting its size and initialising its buttons.
        """
        # Init window
        super().__init__()
        self.setWindowTitle('Salaat Times')
        self.WindowSize = (600, 760)
        self.setGeometry(1500, 300, self.WindowSize[0], self.WindowSize[1]) # x-position, y-position, width, height
        
        # Set widget layout
        widget = QWidget(self)
        self.setCentralWidget(widget)
        self.layout = QGridLayout()
        self.layout.setHorizontalSpacing(20)
        self.layout.setVerticalSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Set margins to 0
        widget.setLayout(self.layout)
        
        # Init program fonts
        self.DefaultFontSize = 30
        self.DefaultLargeFontSize = 55
        self.DefaultTitleFontSize = 70
        self.DefaultFont = "Arial"
        self.TextScalar = 1 # Set proportionally to window size 

        # Get initial prayer time
        self.GetPrayerTimes()
        
        # Populate default buttons
        self.MainPageButtons()
    
    def GetPrayerTimes(self):
        """
        Retrieves prayer times from API (currently hardcoded) and populates relevant instance variables. 
        """
        self.TimeNow = datetime.datetime.now().strftime("%H:%M") # REDUNDANT TODO
        self.DateToday = datetime.datetime.now().strftime("%d/%m/%Y") # REDUNDANT TODO
        self.PrayerTimes = [{"name":"Fujr", "time":"04:21", "font_size": self.DefaultFontSize},
                            {"name":"Sunrise", "time":"06:21", "font_size": self.DefaultFontSize},
                            {"name":"Dhuhr", "time":"12:15", "font_size": self.DefaultFontSize},
                            {"name":"Asr", "time":"15:18","font_size": self.DefaultFontSize},
                            {"name":"Maghrib", "time":"18:03","font_size": self.DefaultFontSize},
                            {"name":"Isha", "time":"19:25","font_size": self.DefaultFontSize},
                            {"name":"Midnight", "time":"23:23","font_size": self.DefaultFontSize}] # TEMP. TODO: add method to get prayer times from API
        self.NameOfNext = "Fujr"
        self.TimeOfNext = datetime.datetime.now() + datetime.timedelta(minutes=126)
        self.TimeTilNext = self.TimeOfNext - datetime.datetime.now()  # TODO should be calculated
    
    def MainPageButtons(self):
        # nRows x 5Col grid
        
        maxGridCols = 5
        self.AllWidgets = {}
        
        # Current Date
        label = QLabel(datetime.datetime.now().strftime("%d/%m/%Y"), self)
        label.setFont(QFont(self.DefaultFont, self.DefaultFontSize))
        label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label, 1, 1, 1, maxGridCols)
        self.AllWidgets["CurrentDate"] = {"Widgets": [label], "Font": self.DefaultFont, "FontSize": self.DefaultFontSize}
        
        # Current Time
        label = QLabel(datetime.datetime.now().strftime("%H:%M:%S"), self)
        label.setFont(QFont(self.DefaultFont, self.DefaultLargeFontSize))
        label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label, 2, 1, 1, maxGridCols)
        self.AllWidgets["CurrentTime"] = {"Widgets": [label], "Font": self.DefaultFont, "FontSize": self.DefaultLargeFontSize}
        
        # Time until next prayer
        hoursTilNext = divmod(self.TimeTilNext.total_seconds(), 60**2) 
        label = QLabel("Time until {}: {}h:{}m".format(self.NameOfNext, int(hoursTilNext[0]), int(hoursTilNext[1]/60)), self)
        label.setFont(QFont(self.DefaultFont, self.DefaultFontSize))
        label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label, 3, 1, 1, maxGridCols)
        self.AllWidgets["TimeTilNext"] = {"Widgets": [label], "Font": self.DefaultFont, "FontSize": self.DefaultFontSize}
        
        # Add seperating line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(line.sizePolicy().hasHeightForWidth())
        line.setSizePolicy(sizePolicy)
        line.setLineWidth(5)
        self.layout.addWidget(line, 4, 1, 1, maxGridCols)
        self.AllWidgets["HLine"] = {"Widgets": [line], "Font": None, "FontSize": None, "lineWidth": 5}
        
        #Prayer times
        for time in self.PrayerTimes:
            prayerName = QLabel(time["name"], self)
            prayerName.setFont(QFont(self.DefaultFont, self.DefaultLargeFontSize))
            prayerName.setAlignment(Qt.AlignRight)
            self.layout.addWidget(prayerName, len(self.AllWidgets)+ 1, 1, 1, 2)
            
            colon = QLabel(":", self)
            colon.setFont(QFont(self.DefaultFont, self.DefaultLargeFontSize))
            colon.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(colon, len(self.AllWidgets)+ 1, 3, 1, 1)
            
            prayerTime = QLabel(time["time"], self)
            prayerTime.setFont(QFont(self.DefaultFont, self.DefaultLargeFontSize))
            prayerTime.setAlignment(Qt.AlignLeft)
            self.layout.addWidget(prayerTime, len(self.AllWidgets) + 1, 4, 1, 2)
            
            self.AllWidgets[time["name"]] = {"Widgets": [prayerName, colon, prayerTime], "Font": self.DefaultFont, "FontSize": self.DefaultLargeFontSize}
        
        
    def resizeEvent(self, event):      
            new_size = event.size()
            
            # Update font sizes based on smaller height or width
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
                
                
                """if widget.__class__.__name__ == 'list':
                    for subwidget in widget:
                        if subwidget.__class__.__name__ == 'QLabel':
                            subwidget.setFont(QFont(self.DefaultFont, self.DefaultFontSize))
                if widget.__class__.__name__ == 'QLabel':
                    widget.setFont(QFont(self.DefaultFont, self.DefaultFontSize))"""
            
            
                
            
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    adhaanApp = AdhaanApp()
    adhaanApp.show()
    sys.exit(app.exec_())
