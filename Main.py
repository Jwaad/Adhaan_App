import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class AdhaanApp(QWidget):
    
    def __init__(self):
        super().__init__()
        self.window_size = (500, 400)
        self.default_font_size = 18
        self.default_large_font_size = 24
        self.default_title_font_size = 30
        self.initWindow()
        self.initButtons()

    def initWindow(self):
        self.setWindowTitle('Salaat Times')
        self.setGeometry(100, 100, self.window_size[0], self.window_size[1]) # x-position, y-position, width, height
        
    def initButtons(self):
        # Set program to grid layout
        layout = QGridLayout()
        self.setLayout(layout)

        # Populate list of buttons
        self.icons = []
        for i in range(0, 10):
            button = QPushButton("Button {}".format(i), self)
            button.clicked.connect(lambda checked, index=i: self.onButtonPress("Button {}".format(index)))
            #text.setAlignment(Qt.AlignCenter)
            layout.addWidget(button, i, 1)
            self.icons.append(button)
        
        # Add the side buttons
        wing1 = QPushButton("<", self)
        wing1.clicked.connect(lambda checked: self.onButtonPress("Left Wing") )
        wing1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)  # Set size policy
        #wing1.setFixedWidth(30)  # Set fixed width
        layout.addWidget(wing1, 2, 0, 7, 1)

        wing2 = QPushButton(">", self)
        wing2.clicked.connect(lambda checked: self.onButtonPress("Right Wing") )
        wing2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)  # Set size policy
        #wing2.setFixedWidth(30)  # Set fixed width
        layout.addWidget(wing2, 2, 2, 7, 1)

        
        # Init all button's font size 
        self.resizeButtonFonts(self.icons, self.default_font_size)

    # temp
    def onButtonPress(self, Text = " "):
        print(Text)
    
    # On resize window
    def resizeEvent(self, event):
        new_size = event.size()
        
        # Get changes in height and width, and use the lower change
        height_increase = new_size.height() / self.window_size[0]
        width_increase = new_size.width() / self.window_size[1]
        
        new_font_size = int(round(self.default_font_size * width_increase, 0))
        if height_increase < width_increase: 
            new_font_size = int(round(self.default_font_size * height_increase, 0))
        
        # Rescale onscreen buttons to new window size
        self.resizeButtonFonts(self.icons, new_font_size)
        
    # 
    def resizeButtonFonts(self, buttons, size, font = "Arial"):
        # Rescale all button fonts
        buttonFont = QFont(font, size, QFont.Bold)
        for button in buttons:
            button.setFont(buttonFont)

def main():
    app = QApplication(sys.argv)
    adhaanApp = AdhaanApp()
    adhaanApp.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()