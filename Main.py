# Written by Jwaad Hussain 2025
#
#   HIGH PRIOIRTY----------------------
#   Alarms / adthaans #   Reminder / ding ding
#   Setting page, multiple customisations Settings button OPTIONS MENU FOR CUSTOMISATION
#   prayer time popups
#   Next day after midnight (On next day, add small +1 icon next to date, until 12am)
#   Create my own title bar
#   Add pop up to refuse to open when already running
#
#   LOW PRIORITY-----------------------
#   Experiment with style: colours and bolding
#   DOWNLOAD WHOLE REST OF MONTH TO MEMORY
#   OTHER PRAYER CALCS (specifically kenya calc)
#   pin to top
#   Tray info, mins remaing / colour for urgency
#   have alternative options, for displaying thirds, in line, or in tooltip
#   Rare cases seconds can get skipped -> timer not synced with system time.
#   Make app close all other instances before opening, or refuse to open, and warn user.
#   Make a fake clock during debug mode, that ticks each second
#
#   Known Bugs--------------------------
#   strange horizontal minimizing behaviour Seems to be a windows thing, cant corner drag, horizontal length stuck to len at drag
#   With multiple monitors, might start on a screen that no longer exists. I.E. starts off screen.add()
#   Windows + arrow key makes UI black. Not sure why, maybe due to resizing code? (happened once and not again)
#   Dist version doesn't run in tray (Solved itself)
#   increase amount of cols, to make ? icon smaller. Or change it's horizontal resizing policy (only happens when UI small)
#
#   Known Issues------------------------
#   Quitting from system tray, doesnt cause app to open into system tray next start
#   Loading audio causes app to start slowly


# BUILD COMMAND: 
# pyinstaller .\Main.py --clean --i=./AdthaanAppIcons/icon.ico --windowed --add-data="./AdthaanAppIcons/*;AdthaanAppIcons/."  --add-data="./AdthaanAppMedia/*;AdthaanAppMedia/."
# ICON TO ICO: https://icoconvert.com/

from doctest import debug
import sys
import datetime
from venv import logger
import requests
import json
import signal
import time
import logging
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import QSound

class AdhaanApp(QMainWindow):
    def __init__(self):
        """
        Initialises the Salaat Times window, setting its size and initialising its buttons.
        """
        # Init QWidgets
        super().__init__()
        
        #Debug mode
        self.DebugMode = True
        self.DebugTime = "2025-03-20 04:21:50"
        self.DebugTime = datetime.datetime.strptime(self.DebugTime, "%Y-%m-%d %H:%M:%S")
        self.PreviousMin = datetime.datetime.now().strftime("%M")
        if self.DebugMode == True:
            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
            print("Debug mode enabled")
            self.PreviousMin = self.DebugTime.strftime("%M")
            
        # Check if another instance is running
        self.SharedMemory = QSharedMemory("AdthaanAppHussain")
        # Create if shared memory does not already exist
        size = 1024  # Size in bytes
        if self.SharedMemory.create(size): #Returns true if succesfully created (false if it already exists)
            print("Created shared memory segment")
            #self.SharedMemory.lock()  # Lock the memory before accessing it
            #Access data here if want to
            self.SharedMemory.unlock() # Unlock when you're done
        else:
            print("Shared Memory already exists, quiting...")
            # TODO add popup here
            adhaanApp.close()
            QApplication.quit()  
            sys.exit(0)
    
        
        # Init window
        self.setWindowTitle('Salaat Times')
        self.WindowSize = (300, 500) # (width, height)
        self.setGeometry(1500, 300, self.WindowSize[0], self.WindowSize[1]) # x-position, y-position, width, height
        self.WinHeightAtPreviousResize = self.WindowSize[1]
        
        # Sort out paths
        try:
            self.BasePath = sys._MEIPASS
        except Exception:
            self.BasePath = "."
        iconPath = self.BasePath + "/AdthaanAppIcons/icon.png"
        mediaPath = self.BasePath + "/AdthaanAppMedia/"
        
        self.setWindowIcon(QIcon(iconPath))
        
        # Load audio into memory, MAKES THE APP LAG on start, MAYBE I THREAD THIS?
        self.AdhanSound = QSound(mediaPath + "/Adthaan/Adthaan_1.wav")  # Load the sound file
        self.ReminderSound = QSound(mediaPath + "Alert.wav") #Load reminder file
        self.ReminderPlayed = False
        self.AdthaanPlayed = False        

        # Setup tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(iconPath))
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
        
        #Set style sheet
        self.ColourSchemes ={"Monokai":{"name":"Monokai", "background":"#202A25", "text":"#C4EBC8",
                            "accent1":"#F6C0D0", "accent2":"#D0A5C0", "accent3":"#8E7C93"},
                            
                            "TrafficLight":{"name":"TrafficLight", "background":"#264653", "text":"#e76f51",
                            "accent1":"#e9c46a", "accent2":"#f4a261", "accent3":"#2a9d8f"},
                            
                            "GreyGreen":{"name":"GreyGreen", "background":"#dad7cd", "text":"#344e41",
                            "accent1":"#588157", "accent2":"#3a5a40", "accent3":"#a3b18a"},
                            
                            "PurplePink":{"name":"PurplePink", "background":"#231942", "text":"#e0b1cb",
                            "accent1":"#9f86c0", "accent2":"#be95c4", "accent3":"#5e548e"},
                            }
        self.ColourScheme = self.ColourSchemes["TrafficLight"]
        self.setWindowOpacity(1)
        self.SetDefaultStyleSheet()        
        
        # Get initial prayer times
        self.DefaultAPI = "http://www.londonprayertimes.com/api/times/"
        self.APIKey = "17522509-896f-49b7-80c8-975c4be643b4"
        self.GetPrayerTimes()
        
        # Populate default buttons
        #time.sleep(3) # Sleep before loading UI, to let above load and calculate facelessly
        self.MainPageButtons()
        
        # Initial time update
        self.OnSecondChange()
        self.UpdateTilUntilNextPrayer()

        # Timer to update clock every second
        self.SecondTimer = QTimer(self)
        self.SecondTimer.timeout.connect(self.OnSecondChange)
        self.SecondTimer.start(1000)  # 1000 ms = 1 second
        
        # Load Save data
        self.LoadSaveData()
        self.MouseStartPos = None
    
    def SetDefaultStyleSheet(self):
        # Colour scheme : #202A25 #C4EBC8 #8E7C93 #D0A5C0 #F6C0D0
        StyleText = """
                        background-color: {}; 
                        color: {};        /* Dark text */
                    """.format(self.ColourScheme["background"], self.ColourScheme["text"])

        if self.DebugMode:
            StyleText += "\n border: 1px solid rgba(255, 0, 0, 30);"
            
        self.setStyleSheet(StyleText)

    def SetToolTipStyleSheet(self, Widget):  
        """
        Sets the style sheet for tooltips.
        """
        Widget.setStyleSheet(f"""
                                QLabel {{
                                    color: {self.ColourScheme["accent2"]}; /* This is currently redundant, as ? icon is white only */
                                }}
                                QToolTip {{
                                    color: {self.ColourScheme["text"]}; 
                                    background-color: {self.ColourScheme["background"]}; 
                                    border: 1px solid {self.ColourScheme["accent1"]};
                                    border-radius: 4px;
                                    font: {self.DefaultFontSize}pt {self.DefaultFont};
                                }}
                            """)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.MouseStartPos = event.globalPos()  # Store initial click position

    def mouseMoveEvent(self, event):
        if self.MouseStartPos:
            delta = event.globalPos() - self.MouseStartPos  # Calculate movement
            self.move(self.x() + delta.x(), self.y() + delta.y())  # Move window
            self.MouseStartPos = event.globalPos()  # Update position

    def mouseReleaseEvent(self, event):
        self.MouseStartPos = None  # Reset when mouse is released
    
    def LoadSaveData(self):
        try:
            with open('data.json', 'r') as f:
                self.SaveData = json.loads(f.read())
        except FileNotFoundError:
            self.SaveData = {"window_pos": [1500, 300], "window_size": self.WindowSize}
            json.dumps(self.SaveData, ensure_ascii=False)
        except json.JSONDecodeError:
            self.SaveData = {"window_pos": [1500, 300], "window_size": self.WindowSize}
            json.dumps(self.SaveData, ensure_ascii=False)
        except:
            self.SaveData = {"window_pos": [1500, 300], "window_size": self.WindowSize}
            json.dumps(self.SaveData, ensure_ascii=False)
        finally:
            self.setGeometry(self.SaveData["window_pos"][0],self.SaveData["window_pos"][1], self.SaveData["window_size"][0], self.SaveData["window_size"][1]) # x-position, y-position, width, height
            self.FitWindowToContentWidth()
    
    def FitWindowToContentWidth(self):
        #print("fitting width to content")
        # Dictionary to keep track of the total width of each row
        row_widths = {}

        # Loop through all items in the layout
        for i in range(self.layout.count()):
            # Get the widget in this layout item
            item = self.layout.itemAt(i)

            # If it's a widget (and not a spacer or stretch)
            if item and item.widget():
                widget = item.widget()

                # Get the row and column position of the item
                row= self.layout.getItemPosition(i)[0]

                # Add the widget's width to the total width of its row
                widget_width = widget.sizeHint().width()
                #print("Content in row {}, ind {} is {} / {}".format(row, i, widget.minimumSizeHint().width(), widget.sizeHint().width()))

                # add to correct row total width
                if row not in row_widths:
                    row_widths[row] = 0
                row_widths[row] += widget_width  # Sum up widths for this row
        
        # Get the maximum width of any row
        max_width = max(row_widths.values(), default=0)
        self.setMinimumWidth(0)
        self.resize(max_width, self.height())  # Resize width to content, but keep current height
        
        
    def SaveUserData(self):
        self.SaveData["window_pos"] = [self.pos().x(), self.pos().y()]
        self.SaveData["window_size"] = [self.size().width(), self.size().height()]
        with open('data.json', 'w') as saveFile:
            json.dump(self.SaveData, saveFile, ensure_ascii=False)
        
    def closeEvent(self, event):
        """On close do some processes"""
        self.SaveUserData()
        
    def OnTrayIconActivation(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.RestoreWindowFromTray()  # Restore the window if double-clicked
            self.setWindowState(Qt.WindowNoState)
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
        
    def OnSecondChange(self):
        """Updates the QLabel with the current time each second"""
        timeNow = datetime.datetime.now()
        if self.DebugMode == True:
            self.DebugTime = self.DebugTime + datetime.timedelta(seconds=1)
            timeNow = self.DebugTime
            
        #self.AllWidgets["CurrentTime"]["Widgets"][0].setText(timeNow.strftime("%H:%M:%S"))
        self.AllWidgets["CurrentTime"]["Widgets"][0].setText(timeNow.strftime("%H:%M"))
        
        minsLeft = self.UpdateTilUntilNextPrayer()
         
        # Update prayer time each minute
        minNow = timeNow.strftime("%M")
        if minNow != self.PreviousMin:
            self.OnMinuteChange(minsLeft, self.PreviousMin, minNow)
            self.PreviousMin = minNow

         
    def OnMinuteChange(self, minsLeft: int, prevMin = 0 , currentMin = 0 ):
        """Code to run on min change

        Args:
            minsLeft (int): time left until next prayer in mins
            prevMin (int): min that it was for logging
            currentMin (int): min that it is now also for logging
        """
        
        logger.debug("Minutes changed from %s to %s", prevMin, currentMin)
        
        if not self.ReminderPlayed and minsLeft <= 15:
            logger.info("Playing reminder sound")
            self.ReminderSound.play()
            self.ReminderPlayed = True
        
        #Trigger on prayer chagnge
        #if smn smn
            #self.OnPrayerTimeChange()
       
        
    
    def OnPrayerTimeChange(self):
        """
        Set of events and triggers that should occur on prayer time change
        """        
        self.ReminderPlayed = False
        self.AdthaanPlayed = False

    def UpdateTilUntilNextPrayer(self) -> int:
        """
        Updates the QLabel with the current time.
        Returns the time left until the next prayer in minutes
        """
        # TODO add check for change of prayer time
        
        timeNow = datetime.datetime.now()
        if self.DebugMode == True:
            timeNow = self.DebugTime
       
        # Starting from Fujr, loop through all prayer times, and the first that is higher than current time is the next prayer
        timeFound = False
        for prayer in self.PrayerTimes.values():
            prayerDatetime = datetime.datetime.strptime(timeNow.strftime("%Y-%m-%d") + prayer["time"], "%Y-%m-%d%H:%M")
            if timeNow <= prayerDatetime:
                timeTilNext = prayerDatetime - timeNow + datetime.timedelta(seconds=60)
                formattedTimeTilNext = str(timeTilNext).split(":")
                prevTimeUntil = self.AllWidgets["TimeUntilNextPrayer"]["Widgets"][0].text() # FOR DEBUG LOG
                newTimeUntilNext = "Time until {}: {}h {}m {}s".format(prayer["name"],formattedTimeTilNext[0], formattedTimeTilNext[1],formattedTimeTilNext[2][:2])
                #newTimeUntilNext = "Time until {}: {}h {}m".format(prayer["name"],formattedTimeTilNext[0], formattedTimeTilNext[1])
                self.AllWidgets["TimeUntilNextPrayer"]["Widgets"][0].setText(newTimeUntilNext)
                timeFound = True
                break
        #Swap to next days prayer times, or do that automatically after 12
        if not timeFound:
            print("WE ARE OUT OF PRAYER TIMES FOR TODAY, HANDLE THIS")
            
        logger.debug("TimeUntilNextPrayer changed from %s to %s", prevTimeUntil, newTimeUntilNext)
        return int(timeTilNext.seconds / 60)
        
    def GetPrayerTimes(self):
        """
        Retrieves prayer times from API (currently hardcoded) and populates relevant instance variables. 
        """
        timeNow = datetime.datetime.now()
        if self.DebugMode == True:
            timeNow = self.DebugTime
        
        # Call API and get todays prayer times
        year = timeNow.strftime("%Y")
        month = timeNow.strftime("%m")
        day = timeNow.strftime("%d")
        tomorrow =  (timeNow + datetime.timedelta(days=1))
        response = requests.get("http://www.londonprayertimes.com/api/times/?format=json&24hours=true&year={}&month={}&key={}".format(year, month, self.APIKey))
        apiResponse = response.json()
        todaysPrayerTimes = apiResponse["times"][timeNow.strftime("%Y-%m-%d")]
        tommorowsPrayerTimes = apiResponse["times"][tomorrow.strftime("%Y-%m-%d")]
        # print(response.status_code) # TODO handle error codes here
        
        # Get islamic midnight time -> NOTE: display today's fujr, but calculate midnight using tomorrow's fujr
        datetimeMaghrib = datetime.datetime.strptime(year + "-" + month + "-" + day + todaysPrayerTimes["magrib"], "%Y-%m-%d%H:%M")
        datetimeFujr = datetime.datetime.strptime(year + "-" + month + "-" + tomorrow.strftime("%d") + tommorowsPrayerTimes["fajr"], "%Y-%m-%d%H:%M")
        maghribToFujr = ( datetimeFujr - datetimeMaghrib)
        midnight = (datetimeMaghrib +  (maghribToFujr / 2) ).strftime("%H:%M")
        firstThird = (datetimeMaghrib +  (maghribToFujr / 3) ).strftime("%H:%M")
        lastThird = (datetimeMaghrib +  ((maghribToFujr / 3) * 2) ).strftime("%H:%M")
        #print(timeNow, (datetimeMaghrib +  (maghribToFujr / 2) ))
        
        #store prayer times in dict
        self.PrayerTimes = {"Fajr":{"name":"Fujr", "time":todaysPrayerTimes["fajr"], "font_size": self.DefaultFontSize},
                            "Sunrise":{"name":"Sunrise", "time":todaysPrayerTimes["sunrise"], "font_size": self.DefaultFontSize},
                            "Dhuhr":{"name":"Dhuhr", "time":todaysPrayerTimes["dhuhr"], "font_size": self.DefaultFontSize},
                            "Asr":{"name":"Asr", "time":todaysPrayerTimes["asr"],"font_size": self.DefaultFontSize},
                            "Maghrib":{"name":"Maghrib", "time":todaysPrayerTimes["magrib"],"font_size": self.DefaultFontSize},
                            "Isha":{"name":"Isha", "time":todaysPrayerTimes["isha"],"font_size": self.DefaultFontSize},
                            "Midnight":{"name":"Midnight", "time":midnight,"font_size": self.DefaultFontSize},
                            "FirstThird":{"name":"FirstThird", "time":firstThird,"font_size": self.DefaultFontSize},
                            "LastThird":{"name":"LastThird", "time":lastThird,"font_size": self.DefaultFontSize}}

    def MainPageButtons(self):
        
        # Add info icon
        def createToolTip(toolTipText):
            """
            Creates a tool tip for the info icon.
            """
            infoIcon = QLabel("❔", self) #
            infoIcon.setFont(QFont(self.DefaultFont, self.DefaultFontSize))
            infoIcon.setAlignment(Qt.AlignTop | Qt.AlignLeft )
            infoIcon.setSizePolicy(standardSizePolicy)
            infoIcon.setToolTip(toolTipText)
            self.SetToolTipStyleSheet(infoIcon) # TODO combine with createToolTip
            return infoIcon
        
        self.AllWidgets = {}
        
        smallRowSpan = 1
        normalRowSpan = 2
        normalColSpan = 1
        maxColSpan = 5
        
        timeNow = datetime.datetime.now()
        if self.DebugMode == True:
            timeNow = self.DebugTime
            
        standardSizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Ignored)
        self.TimeWidgets = [
            #CurrentDate #202A25 #C4EBC8 #8E7C93 #D0A5C0 #F6C0D0
            {"name":"CurrentDate", "default_text":timeNow.strftime("%d/%m/%Y"), "type":QLabel,
             "alignment":Qt.AlignCenter,"size_policy":standardSizePolicy, "row_span":smallRowSpan,
             "col_span":maxColSpan, "font_size":self.DefaultFontSize},
            #CurrentTime
            {"name":"CurrentTime", "default_text":timeNow.strftime("%H:%M:%S"), "type":QLabel,
             "alignment":Qt.AlignCenter,"size_policy":standardSizePolicy, "row_span":normalRowSpan,
             "col_span":maxColSpan, "font_size":self.DefaultLargeFontSize, "font_color":"{}".format(self.ColourScheme["accent1"])},
            #TimeUntilNextPrayer
            {"name":"TimeUntilNextPrayer", "default_text": "Time Until ?: ?h ?m", "type":QLabel,
             "alignment":Qt.AlignCenter,"size_policy":standardSizePolicy, "row_span":smallRowSpan,
             "col_span":maxColSpan, "font_size":self.DefaultFontSize}]
        
        # Populate time widgets
        rows = 1
        for widget in self.TimeWidgets:
            label = widget["type"](widget["default_text"], self)
            label.setFont(QFont(self.DefaultFont, widget["font_size"]))
            label.setSizePolicy(widget["size_policy"])
            if widget["type"] == QLabel:
                label.setAlignment(widget["alignment"])
                if "font_color" in widget:
                    label.setStyleSheet("color: " + widget["font_color"])
            elif widget["type"] == QFrame:
                line.setLineWidth(widget["line_width"])
            self.layout.addWidget(label, rows, 1, widget["row_span"], widget["col_span"])
            self.AllWidgets[widget["name"]] = {"Widgets": [label], "Font": self.DefaultFont, "FontSize": widget["font_size"]}
            rows += widget["row_span"]
        
        # Add seperating line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        lineSizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        line.setSizePolicy(lineSizePolicy)
        line.setLineWidth(5)
        self.layout.addWidget(line, rows, 1, smallRowSpan, maxColSpan)
        self.AllWidgets["HLine"] = {"Widgets": [line], "Font": None, "FontSize": None, "lineWidth": 5}
        rows += smallRowSpan

        # Populate Prayer times
        for time in self.PrayerTimes.values():
            
            # Dont make widgets for first and last third
            if time["name"] == "FirstThird" or time["name"] == "LastThird":
                continue
            
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

            # Add tool tip to specific prayer times
            if time["name"] == "Isha":
                # Calculate first third
                infoIcon = createToolTip("First third starts at:\n{}".format(self.PrayerTimes["FirstThird"]["time"]))
                self.layout.addWidget(infoIcon, rows, 6, normalRowSpan, 1)
                self.AllWidgets["IshaToolTip"] = {"Widgets": [infoIcon], "Font": self.DefaultFont, "FontSize": self.DefaultFontSize}
            if time["name"] == "Midnight":
                # Calculate first third
                infoIcon = createToolTip("Last third starts at:\n{}".format(self.PrayerTimes["LastThird"]["time"]))
                self.layout.addWidget(infoIcon, rows, 6, normalRowSpan, 1)
                self.AllWidgets["MidnightToolTip"] = {"Widgets": [infoIcon], "Font": self.DefaultFont, "FontSize": self.DefaultFontSize}

            rows += normalRowSpan
            self.AllWidgets[time["name"]] = {"Widgets": [prayerName, colon, prayerTime], "Font": self.DefaultFont, "FontSize": self.DefaultLargeFontSize}

    def resizeEvent(self, event):
            new_size = event.size()
            stepSize = 10
            if abs(self.WinHeightAtPreviousResize - new_size.height()) < stepSize:
                return
            
            # Update font sizes based on height change
            self.TextScalar = new_size.height() / self.WindowSize[1] # % increase of height
            
            # Update font sizes of each widget if applicable
            for key in self.AllWidgets.keys():
                
                for widget in self.AllWidgets[key]["Widgets"]:
                    if widget.__class__.__name__ == 'QLabel':
                        widget.setFont(QFont(self.AllWidgets[key]["Font"], int(round(self.AllWidgets[key]["FontSize"] * self.TextScalar, 0))))
            
            self.WinHeightAtPreviousResize = new_size.height() 

if __name__ == '__main__':
    
    def handle_keyboard_interrupt(signal, frame):
        print("Keyboard Interrupt. Application closed.")
        adhaanApp.close()
        QApplication.quit()  
        sys.exit(0)
    
    # Set up signal handler to catch keyboard interrupt
    signal.signal(signal.SIGINT, handle_keyboard_interrupt)

    try:
        app = QApplication(sys.argv)
        adhaanApp = AdhaanApp()
        adhaanApp.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)  # Exit if something else goes wrong
        
    
