import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class AdhaanApp(QWidget):
    
    def __init__(self):
        super().__init__()
        self.window_size = (300, 200)
        self.default_font_size = 12
        self.initWindow()
        self.initButtons()

    def initWindow(self):
        self.setWindowTitle('Simple PyQt5 Example')
        self.setGeometry(100, 100, self.window_size[0], self.window_size[1]) # x-position, y-position, width, height
        

    def initButtons(self):
        # Set program to grid layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Init button 1
        button1 = QPushButton('Button 1', self)
        button1.clicked.connect(lambda:self.onButtonPress("button1"))
        layout.addWidget(button1, 0)
         
        # Init button 1
        button2 = QPushButton('Button 2', self)
        button2.clicked.connect(lambda:self.onButtonPress("button2"))
        layout.addWidget(button2, 1)
        
        self.buttons = [button1, button2]
        
        # Init all button's font size
        self.resizeButtonFonts(self.default_font_size)


    def onButtonPress(self, Text = " "):
        print(Text)
        
    def resizeEvent(self, event):
        new_size = event.size()
        
        # Get changes in height and width, and use the lower change
        height_increase = new_size.height() / self.window_size[0]
        width_increase = new_size.width() / self.window_size[1]
        
        new_font_size = int(round(self.default_font_size * width_increase, 0))
        if height_increase < width_increase:
            new_font_size = int(round(self.default_font_size * height_increase, 0))
        
        # Rescale onscreen buttons to new window size
        self.resizeButtonFonts(new_font_size)
        
        
    def resizeButtonFonts(self, size, font = "Arial"):
        # Rescale all button fonts
        font = QFont(font, size, QFont.Bold)
        for button in self.buttons:
            button.setFont(font)

def main():
    app = QApplication(sys.argv)
    adhaanApp = AdhaanApp()
    adhaanApp.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()