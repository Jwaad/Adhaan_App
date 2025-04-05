# Written by Jwaad Hussain 2025
# BUILD COMMAND: 
# pyinstaller .\Main.py --clean --i=./AdthaanAppIcons/icon.ico --windowed --add-data="./AdthaanAppIcons/*;AdthaanAppIcons/."  --add-data="./AdthaanAppMedia/*;AdthaanAppMedia/."
# ICON TO ICO: https://icoconvert.com/

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
    def __init__(self, app):
        """
        Initialises the Salaat Times window, setting its size and initialising its buttons.
        """
        # Init QWidgets
        super().__init__()
        self.app = app
        
        #Debug mode
        self.DebugMode = False
        self.DebugTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.DebugTime = "2025-03-20 05:59:55"
        self.DebugTime = datetime.datetime.strptime(self.DebugTime, "%Y-%m-%d %H:%M:%S")
        self.PreviousMin = (datetime.datetime.now() - datetime.timedelta(minutes=1) ).strftime("%M")
        if self.DebugMode == True:
            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
            print("Debug mode enabled")
            self.PreviousMin = (self.DebugTime - datetime.timedelta(minutes=1) ).strftime("%M")
        
        # Sort out paths
        try:
            self.BasePath = sys._MEIPASS
        except Exception:
            self.BasePath = "."
        iconPath = self.BasePath + "/AdthaanAppIcons/icon.png"
        mediaPath = self.BasePath + "/AdthaanAppMedia/"
        
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
        
        # Init program fonts
        self.DefaultFontSize = 15
        self.DefaultLargeFontSize = 30
        self.DefaultTitleFontSize = 50
        self.DefaultFont = "Verdana"
        
        # Check if another instance is running
        self.SharedMemory = QSharedMemory("AdthaanAppHussain")
        size = 1024  # Size in bytes
        if not self.SharedMemory.create(size): # If couldnt create, another instance is running
            self.AlreadyRunningDialogBox(iconPath)
            QApplication.quit()  
            sys.exit(0)
            
        # Init window
        self.setWindowTitle('Salaat Times')
        self.WindowSize = (300, 500) # (width, height)
        self.setGeometry(1500, 300, self.WindowSize[0], self.WindowSize[1]) # x-position, y-position, width, height
        self.WinHeightAtPreviousResize = self.WindowSize[1]
        self.setWindowIcon(QIcon(iconPath))
        
        self.setWindowOpacity(1)
        self.SetDefaultStyleSheet() 
        self.setWindowFlags(Qt.WindowStaysOnTopHint) # Qt.Window | Qt.CustomizeWindowHint | 
        
        # Load audio into memory, MAKES THE APP LAG on start, MAYBE I THREAD THIS?
        self.AdthaanSound = QSound(mediaPath + "Adthaan_1.wav")  # Load the sound file
        self.FujrAdthaanSound = QSound(mediaPath + "Fujr_Adthaan_2.wav")  # Load the sound file
        self.ReminderSound = QSound(mediaPath + "Alert.wav") #Load reminder file
        self.ReminderPlayed = False 

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
        # Get initial prayer times
        self.DefaultAPI = "http://www.londonprayertimes.com/api/times/"
        self.APIKey = "17522509-896f-49b7-80c8-975c4be643b4"
        self.PrayerNames = ["Fujr", "Dhuhr", "Asr", "Maghrib", "Isha"]
        self.GetPrayerTimes()
        
        # Populate default buttons
        #time.sleep(3) # Sleep before loading UI, to let above load and calculate facelessly
        self.MainPageButtons()
        
        # Initial time update
        self.CurrentPrayerTime = None
        self.PrevMinsLeft = self.UpdateTilUntilNextPrayer() #+ 1
        self.OnSecondChange()
        
        # Timer that triggers after resize
        self.ResizeTimer = QTimer(self)
        self.ResizeTimer.setSingleShot(True)
        self.ResizeTimer.timeout.connect(self.FitWindowToContentWidth)
        self.ResizeDelay = 500

        # Timer to update clock every second
        self.SecondTimer = QTimer(self)
        self.SecondTimer.timeout.connect(self.OnSecondChange)
        self.SecondTimer.start(1000)
        
        # Load Save data
        self.LoadSaveData()
        self.MouseStartPos = None

    
    def AlreadyRunningDialogBox(self, icon_path):
        msg = QMessageBox()
        msg.setWindowTitle("Adthaan app already running!")
        msg.setWindowIcon(QIcon(icon_path))
        msg.setText("App already running! \nPlease close before reopening.")
        msg.setStandardButtons(QMessageBox.Ok)
        styleSheet = f"""
            QMessageBox {{
                background-color: {self.ColourScheme["background"]};
            }}
            QLabel {{
                font: {self.DefaultFontSize}pt {self.DefaultFont};
                color: {self.ColourScheme["text"]}; 
                
            }}
            QPushButton {{
                background-color: {self.ColourScheme["accent3"]};
                border: 1px solid {self.ColourScheme["accent1"]};
                color: {self.ColourScheme["accent2"]};
                padding: 10px 20px;
                font: {self.DefaultFontSize}pt {self.DefaultFont};
                margin: 4px 2px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {self.ColourScheme["background"]};
            }}
        """
        #Apply and display                            
        msg.setStyleSheet(styleSheet)
        
        #  center-aligned all text
        textLabels = msg.findChildren(QLabel)
        for label in textLabels:
            label.setAlignment(Qt.AlignCenter)

        # center-aligned buttons
        buttonBox = msg.findChild(QDialogButtonBox)
        if buttonBox:
            buttonBox.setCenterButtons(True)
        msg.exec_()
    
    def SetDefaultStyleSheet(self):
        # Colour scheme : #202A25 #C4EBC8 #8E7C93 #D0A5C0 #F6C0D0
        StyleText = f"""
                        background-color: {self.ColourScheme["background"]}; 
                        color: {self.ColourScheme["text"]};        /* Dark text */
                    """

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
        print("fiting content to width")
        # Get width of each rows content
        rowWidths = self.GetContentWidthByRow()
        # Get the largest width
        max_width = max(rowWidths.values(), default=0)
        self.setMinimumWidth(0)
        self.resize(max_width, self.height())  # Resize width to content, but keep current height
    
    def GetContentWidthByRow(self):
        # Dictionary to keep track of the total width of each row
        row_widths = {}
        leftMargin, _, rightMargin, _ = self.layout.getContentsMargins()
        print(self.layout.spacing(), leftMargin, rightMargin)
        
        # Loop through all items in the layout
        for i in range(self.layout.count()):
            # Get the widget in this layout item
            item = self.layout.itemAt(i)
            # If it's a widget (and not a spacer or stretch)
            if item and item.widget():
                widget = item.widget()
                # Get the row and column position of the item
                row= self.layout.getItemPosition(i)[0]
                widget_width = widget.sizeHint().width()
                """
                if widget.__class__.__name__ == 'QLabel':
                    # Get font metrics for the label's font
                    font_metrics = QFontMetrics(widget.font())

                    # Get the width and height of the text
                    #text_width = font_metrics.horizontalAdvance(widget.text())
                    text_rect = font_metrics.boundingRect(widget.text())
                    text_width = text_rect.width()

                    widget_width = text_width#widget.sizeHint().width()   #.geometry().width()
                    
                elif widget.__class__.__name__ == "QFrame":
                    # Add the widget's width to the total width of its row
                    widget_width = widget.sizeHint().width()
                """
                    #print("Content in row {}, ind {} is {} / {}".format(row, i, widget.minimumSizeHint().width(), widget.sizeHint().width()))
                if row not in row_widths:
                    row_widths[row] = leftMargin + rightMargin
                row_widths[row] += widget_width  # Sum up widths for this row
        return row_widths
        
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
        
        #Update clock Widget
        #self.AllWidgets["CurrentTime"]["Widgets"][0].setText(timeNow.strftime("%H:%M:%S"))
        self.AllWidgets["CurrentTime"]["Widgets"][0].setText(timeNow.strftime("%H:%M"))
        
        # Update time left until next prayer
        minsLeft = self.UpdateTilUntilNextPrayer()
        # if minsLeft is none, dont execute OnMinuteChange
        if minsLeft == None:
            return
            
        # Update prayer time each minute
        minNow = timeNow.strftime("%M")
        if minNow != self.PreviousMin:            
            self.OnMinuteChange(minsLeft, self.PreviousMin, minNow)
            self.PreviousMin = minNow
            self.PrevMinsLeft = minsLeft

         
    def OnMinuteChange(self, minsLeft: int, prevMin = 0 , currentMin = 0 ):
        """Code to run on min change

        Args:
            minsLeft (int): time left until next prayer in mins
            prevMin (int): min that it was for logging
            currentMin (int): min that it is now also for logging
        """
        
        logger.debug("MINITE CHANGE TRIGGERED: Minutes changed from %s to %s", prevMin, currentMin)
        
        if not self.ReminderPlayed and minsLeft <= 15:
            logger.info("Playing reminder sound")
            self.ReminderSound.play()
            self.ReminderPlayed = True
        
        #Trigger on prayer chagnge
        if minsLeft > self.PrevMinsLeft:
            self.OnPrayerTimeChange()
       
    def OnPrayerTimeChange(self):
        """
        Set of events and triggers that should occur on prayer time change
        """        
        logger.info("Prayer Time Changed")
        self.ReminderPlayed = False
        # If not a prayer dont play adthaan
        if not self.CurrentPrayerTime in self.PrayerNames:
            logger.info(f"Not Playing Sound as time of : {self.CurrentPrayerTime}")
            return
        
        # For fujr
        if self.CurrentPrayerTime == "Fujr":
            logger.info("Playing Fujr Adthaan Sound")
            self.FujrAdthaanSound.play()
            return
        
        #All other prayers
        logger.info("Playing Regular Adthaan Sound")
        self.AdthaanSound.play()
        

    def UpdateTilUntilNextPrayer(self) -> int:
        """
        Updates the QLabel with the current time.
        Returns the time left until the next prayer in minutes
        """
        timeTilNext = None 
        timeNow = datetime.datetime.now()
        if self.DebugMode == True:
            timeNow = self.DebugTime
       
        # Starting from Fujr, loop through all prayer times, and the first that is higher than current time is the next prayer
        timeFound = False
        for prayer in self.PrayerTimes.values():
            prayerDatetime = prayer["time"]
            #datetime.datetime.strptime(timeNow.strftime("%Y-%m-%d") + prayer["time"], "%Y-%m-%d%H:%M")
            
            # Ignore first and last thirds
            if prayer["name"] == "FirstThird" or prayer["name"] == "LastThird":
                continue
            
            if timeNow < prayerDatetime:
                
                # distance between now and this prayer
                timeTilNext = prayerDatetime - timeNow
                
                # FOR DEBUG LOG
                timeFound = True
                prevTimeUntil = self.AllWidgets["TimeUntilNextPrayer"]["Widgets"][0].text() 
                
                #Format delta time into hours, minutes and seconds
                formattedTimeTilNext = str(timeTilNext).split(":")
                newTimeUntilNext = "Time until {}: {}h {}m {}s".format(prayer["name"],formattedTimeTilNext[0], formattedTimeTilNext[1],formattedTimeTilNext[2][:2])
                self.AllWidgets["TimeUntilNextPrayer"]["Widgets"][0].setText(newTimeUntilNext)
                break
            self.CurrentPrayerTime = prayer["name"]
            
        #Swap to next days prayer times, or do that automatically after 12
        if timeFound:
            logger.debug("UpdateTilUntilNextPrayer: TimeUntilNextPrayer changed from %s to %s", prevTimeUntil, newTimeUntilNext)
        else:    
            self.CurrentPrayerTime = prayer["name"] = None
            print("WE ARE OUT OF PRAYER TIMES FOR TODAY, HANDLE THIS")
        
        if timeTilNext == None:
            return None
        
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
       
        midnight = (datetimeMaghrib +  (maghribToFujr / 2))
        firstThird = (datetimeMaghrib +  (maghribToFujr / 3))
        lastThird = (datetimeMaghrib +  ((maghribToFujr / 3) * 2))
        
        #store prayer times in dict
        self.PrayerTimes = {"Fujr":{"name":"Fujr", "time":self.HourMinToDateTime(day, month, year, todaysPrayerTimes["fajr"]), "font_size": self.DefaultFontSize},
                            "Sunrise":{"name":"Sunrise", "time":self.HourMinToDateTime(day, month, year, todaysPrayerTimes["sunrise"]), "font_size": self.DefaultFontSize},
                            "Dhuhr":{"name":"Dhuhr", "time":self.HourMinToDateTime(day, month, year, todaysPrayerTimes["dhuhr"]), "font_size": self.DefaultFontSize},
                            "Asr":{"name":"Asr", "time":self.HourMinToDateTime(day, month, year, todaysPrayerTimes["asr"]),"font_size": self.DefaultFontSize},
                            "Maghrib":{"name":"Maghrib", "time":self.HourMinToDateTime(day, month, year, todaysPrayerTimes["magrib"]),"font_size": self.DefaultFontSize},
                            "Isha":{"name":"Isha", "time":self.HourMinToDateTime(day, month, year, todaysPrayerTimes["isha"]),"font_size": self.DefaultFontSize},
                            "FirstThird":{"name":"FirstThird", "time":firstThird,"font_size": self.DefaultFontSize},
                            "Midnight":{"name":"Midnight", "time":midnight,"font_size": self.DefaultFontSize},
                            "LastThird":{"name":"LastThird", "time":lastThird,"font_size": self.DefaultFontSize}}
        #for asd in self.PrayerTimes.values():
        #    print(asd)
        
    def HourMinToDateTime(self, day:str, month:str, year:str, hourMinString:str) -> datetime.datetime:
        """Puts together a specified day, month and hour and minute string into a datetime object

        Args:
            day (str): day in format "DD"
            month (str): month in format "MM"
            year (str): year in format "YYYY"
            hourMinString (str): hour and minute in format "HH:MM"

        Returns:
            datetime.datetime: Return datetime.datetime obj of time inputed
        """
        return datetime.datetime.strptime(year + "-" + month + "-" + day + " " + hourMinString, "%Y-%m-%d %H:%M")
        
    
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
            
            prayerTime = time["time"].strftime("%H:%M")
            prayerTime = QLabel(prayerTime, self)
            prayerTime.setFont(QFont(self.DefaultFont, self.DefaultLargeFontSize))
            prayerTime.setAlignment(Qt.AlignLeft)
            prayerTime.setSizePolicy(standardSizePolicy)
            self.layout.addWidget(prayerTime, rows, 4, normalRowSpan, 2)

            # Add tool tip to specific prayer times
            if time["name"] == "Isha":
                # Calculate first third
                infoIcon = createToolTip("First third starts at:\n{}".format(self.PrayerTimes["FirstThird"]["time"].strftime("%H:%M")))
                self.layout.addWidget(infoIcon, rows, 6, normalRowSpan, 1)
                self.AllWidgets["IshaToolTip"] = {"Widgets": [infoIcon], "Font": self.DefaultFont, "FontSize": self.DefaultFontSize}
            if time["name"] == "Midnight":
                # Calculate first third
                infoIcon = createToolTip("Last third starts at:\n{}".format(self.PrayerTimes["LastThird"]["time"].strftime("%H:%M")))
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
            #width = max(self.GetContentWidthByRow().values())

            #self.ResizeTimer.start(self.ResizeDelay)
            self.updateGeometry()
            super().resizeEvent(event)

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
        adhaanApp = AdhaanApp(app)
        adhaanApp.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)  # Exit if something else goes wrong
        
    
