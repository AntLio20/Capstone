# File Name: pam.py
# Authors: Javier Chung, Andy Dai, Antonio Lio, Jason Stuckless
# Date: Oct 26, 2024
# Description: This is the GUI page 

# pip3 install pyqt
from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QStackedWidget, QPushButton, QVBoxLayout, QLineEdit, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

import sys
import pam

# this gui allows users to interact and login to their accounts
class LoginWindow(QWidget):
    def __init__(self, stack):
        super().__init__()

        self.stack = stack 

        # setting the background color of the page
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor('#DFDFDF'))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # adding content onto the gui page
        mainLayout = QHBoxLayout() # setting main layout to be horizontal

        # Setting up the layout on the left side
        layoutLeft = QVBoxLayout()
        titleLabel = QLabel("PAM")  # Title or logo
        layoutLeft.addWidget(titleLabel)
        layoutLeft.setAlignment(Qt.AlignCenter)

        mainLayout.addLayout(layoutLeft)

        # Create a QWidget for the right layout and set its background color
        rightWidget = QWidget() 
        rightPalette = rightWidget.palette()  # Get the palette of the new widget
        rightPalette.setColor(QPalette.Window, QColor('#A0C6DC'))  
        rightWidget.setPalette(rightPalette) 
        rightWidget.setAutoFillBackground(True) 

        # setting up the layout on the right side
        layoutRight = QVBoxLayout()

        # creating a label
        self.label = QLabel()

        # setting up input on the GUI
        self.inputUsername = QLineEdit()
        self.inputPassword = QLineEdit()

        self.inputUsername.textChanged.connect(self.label.setText) # the input changes the label
        self.inputPassword.textChanged.connect(self.label.setText) 

        # adding input for the username and password to the layout
        layoutRight.addWidget(self.inputUsername) 
        layoutRight.addWidget(self.inputPassword) 

        layoutRight.addWidget(self.label) # adding a label

        # creating a button with a text and parent widget
        centerBtn = QPushButton(text="Login", parent=self)
        centerBtn.clicked.connect(self.login)
        layoutRight.addWidget(centerBtn) # adding a button
        layoutRight.setAlignment(Qt.AlignCenter)
        
        # setting up how the layouts will be constructed and the width of them
        mainLayout.addLayout(layoutLeft) 
        mainLayout.addLayout(layoutRight)

        # first parameter is the layout (added in a mainLayout in order and second is the strech)
        mainLayout.setStretch(0, 1)  # Left layout
        mainLayout.setStretch(1, 1)  # Right layout

        self.setLayout(mainLayout)


    def login(self):
        # add logic for checking login
        print("Login being checked")

        # go to next page
        self.stack.setCurrentIndex(1)


# this contains the GUI for the main page of our application
class MainPage(QWidget):
    def __init__(self):
        super().__init__()

        # setting the background color
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor('DFDFDF'))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # setting up the layout
        mainLayout = QVBoxLayout()

        pageLayout = QVBoxLayout()

        # retrieving the section headings and meeting notes
        meetingNotesList = pam.getMeetingNotes()
        sectionHeadings = pam.getSectionHeadings()

        # displaying the summarized transcript on the label
        for i in range(0, len(meetingNotesList)):
            # Creating a label and displaying it in the center of the layout
            meetingLabel = QLabel( sectionHeadings[i] + ": " + meetingNotesList[i] + "\n")
            # meetingLabel.setAlignment(Qt.AlignCenter) 

            # adding label to layout
            pageLayout.addWidget(meetingLabel)

        # adding the page to the mainLayout
        mainLayout.addLayout(pageLayout) 


        # stretching the page layout
        mainLayout.setStretch(0, 1)  # Left layout

        # setting the layout to the window
        self.setLayout(mainLayout)

        # Set window properties
        # self.setWindowTitle("Text Display Example")  
        
        def setMeetingSummary(self, text):
            self.meetingLabel.setText(text)

# this class manages the stacked pages
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # The QStackedLayout will store all the different QWidgets/pages
        self.stack = QStackedWidget()
        
        # storing all the pages to the stack
        self.loginPage = LoginWindow(self.stack)
        self.mainPage = MainPage()
        # the way the pages are stored determine thier index
        self.stack.addWidget(self.loginPage) # 0
        self.stack.addWidget(self.mainPage) # 1
        
        # Set the stacked widget as the central widget of QMainWindow
        self.setCentralWidget(self.stack)

        # setting up the default size of the browser
        self.setMinimumSize(800, 600)

# config setup for Qapplication
app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec_())







