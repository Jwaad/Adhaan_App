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
        self.window_size = (600, 760)
        self.setGeometry(1500, 300, self.window_size[0], self.window_size[1]) # x-position, y-position, width, height
        
        # Set widget layout
        widget = QWidget(self)
        self.setCentralWidget(widget)
        self.layout = QGridLayout()
        self.layout.setHorizontalSpacing(20)
        self.layout.setVerticalSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Set margins to 0
        widget.setLayout(self.layout)
        
        # Init program fonts
        self.default_font_size = 30
        self.default_large_font_size = 55
        self.default_title_font_size = 70
        self.default_Font = "Arial"

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
        self.PrayerTimes = [{"name":"Fujr", "time":"04:21"},
                            {"name":"Sunrise", "time":"06:21"},
                            {"name":"Dhuhr", "time":"12:15"},
                            {"name":"Asr", "time":"15:18"},
                            {"name":"Maghrib", "time":"18:03"},
                            {"name":"Isha", "time":"19:25"},
                            {"name":"Midnight", "time":"23:23"}] # TEMP. TODO: add method to get prayer times from API
        self.NameOfNext = "Fujr"
        self.TimeOfNext = datetime.datetime.now() + datetime.timedelta(minutes=126)
        self.TimeTilNext = self.TimeOfNext - datetime.datetime.now()  # TODO should be calculated
    
    def MainPageButtons(self):
        # nRows x 5Col grid
        
        maxGridCols = 5
        allWidgets = []
        
        # Current Date
        label = QLabel(datetime.datetime.now().strftime("%d/%m/%Y"), self)
        label.setFont(QFont(self.default_Font, self.default_font_size))
        label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label, 1, 1, 1, maxGridCols)
        allWidgets.append(label)
        
        # Current Time
        label = QLabel(datetime.datetime.now().strftime("%H:%M:%S"), self)
        label.setFont(QFont(self.default_Font, self.default_large_font_size))
        label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label, 2, 1, 1, maxGridCols)
        allWidgets.append(label)
        
        # Time until next prayer
        hoursTilNext = divmod(self.TimeTilNext.total_seconds(), 60**2) 
        label = QLabel("Time until {}: {}h:{}m".format(self.NameOfNext, int(hoursTilNext[0]), int(hoursTilNext[1]/60)), self)
        label.setFont(QFont(self.default_Font, self.default_font_size))
        label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label, 3, 1, 1, maxGridCols)
        allWidgets.append(label)
        
        # Add seperating line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(line.sizePolicy().hasHeightForWidth())
        line.setSizePolicy(sizePolicy)
        line.setLineWidth(5)
        self.layout.addWidget(line, 4, 1, 1, maxGridCols)
        allWidgets.append(line)
        
        #Prayer times
        for time in self.PrayerTimes:
            prayerName = QLabel(time["name"], self)
            prayerName.setFont(QFont(self.default_Font, self.default_large_font_size))
            prayerName.setAlignment(Qt.AlignRight)
            self.layout.addWidget(prayerName, len(allWidgets)+ 1, 1, 1, 2)
            
            colon = QLabel(":", self)
            colon.setFont(QFont(self.default_Font, self.default_large_font_size))
            colon.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(colon, len(allWidgets)+ 1, 3, 1, 1)
            
            prayerTime = QLabel(time["time"], self)
            prayerTime.setFont(QFont(self.default_Font, self.default_large_font_size))
            prayerTime.setAlignment(Qt.AlignLeft)
            self.layout.addWidget(prayerTime, len(allWidgets) + 1, 4, 1, 2)
            
            # Append to widet list in this format: [PrayerName, Colon, PrayerTime]
            allWidgets.append([prayerName, colon, prayerTime])



if __name__ == '__main__':
    app = QApplication(sys.argv)
    adhaanApp = AdhaanApp()
    adhaanApp.show()
    sys.exit(app.exec_())
