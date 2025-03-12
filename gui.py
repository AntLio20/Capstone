# File Name: pam.py
# Authors: Javier Chung, Andy Dai, Antonio Lio, Jason Stuckless
# Date: Oct 26, 2024
# Description: This is the main page containing the GUI

# pip install PyQt5
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QStackedWidget, QPushButton, QVBoxLayout, QLineEdit, QLabel, QSpacerItem, QHBoxLayout, QSizePolicy, QGraphicsDropShadowEffect, QGridLayout, QFrame, QScrollArea
from PyQt5.QtGui import QDragEnterEvent, QDragLeaveEvent, QDragMoveEvent, QDropEvent, QPalette, QColor, QFont, QPixmap, QCursor, QIcon, QFontMetrics
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtWidgets import QMessageBox

import sys
from FileSystem import FileSystem
import pam
import os
import openai
import speakerDiarization
import Recorder
from login import LoginSystem

# connecting to openai
openai.api_key = os.getenv(
    "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")


# setting up global values
documentFont = QFont("Times New Roman", 12)  # Default font and font size

# Global shadow
shadow = QGraphicsDropShadowEffect()
shadow.setBlurRadius(40)
shadow.setXOffset(10)
shadow.setYOffset(10)
shadow.setColor(QColor(0, 0, 0, 100))

# this gui allows users to interact and login to their accounts
class LoginWindow(QWidget):
    def __init__(self, stack):
        super().__init__()

        self.stack = stack
        self.login_system = LoginSystem()  # Initialize login system
        self.is_login_mode = True  # Flag to toggle between login and register mode

        # Setting the background color of the page
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor('#DFDFDF'))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        self.setStyleSheet("QLabel{color: #000000;}")  # setting the default text color for all labels

        # Adding content onto the gui page
        mainLayout = QHBoxLayout()  # setting main layout to be horizontal

        # Setting up the layout on the left side
        layoutLeft = QVBoxLayout()
        logoImageLabel = QLabel(self)

        # Loading the image
        logo = QPixmap("./images/pamLogo.png")
        logoImageLabel.setPixmap(logo)

        # setting up the size
        logoImageLabel.setScaledContents(True)
        logoImageLabel.setFixedHeight(375)
        logoImageLabel.setFixedWidth(375)
        layoutLeft.addWidget(logoImageLabel)
        layoutLeft.setAlignment(Qt.AlignCenter)

        # setting up the right widget to contain the color
        rightWidget = QWidget()
        rightWidget.setStyleSheet(
            "background-color: #ffffff; border-radius: 10px; font-family: Arial; text-align: center;")

        rightWidget.setGraphicsEffect(shadow)

        # Setting up the layout on the right side to be vertical
        self.layoutRight = QVBoxLayout(rightWidget)
        self.layoutRight.setContentsMargins(50, 25, 50, 25)
        self.layoutRight.setSpacing(20)

        # Create title label for login/register
        self.loginLabel = QLabel("LOGIN")
        loginFont = QFont("Arial", 40, QFont.Bold)
        self.loginLabel.setFont(loginFont)
        self.layoutRight.addWidget(self.loginLabel)

        # Create input widgets
        # Setting up input on the GUI
        self.inputUsername = QLineEdit()  # Variable can be used anywhere in class when self is in the front
        self.inputPassword = QLineEdit()

        # Email field for registration
        self.inputEmail = QLineEdit()
        self.inputEmail.setVisible(False)  # Hidden by default in login mode

        # styling for the inputs
        inputStyle = "background-color: #E8E8E8; color: #7A7A7A; padding: 10px; font-size: 20px;"
        self.inputUsername.setStyleSheet(inputStyle)
        self.inputPassword.setStyleSheet(inputStyle)
        self.inputEmail.setStyleSheet(inputStyle)

        # Setting up placeholder text
        self.inputUsername.setPlaceholderText("Username")
        self.inputPassword.setPlaceholderText("Password")
        self.inputPassword.setEchoMode(QLineEdit.Password)  # Hide password
        self.inputEmail.setPlaceholderText("Email (optional)")

        # adding input for the username and password to the layout
        self.layoutRight.addWidget(self.inputUsername)
        self.layoutRight.addWidget(self.inputPassword)
        self.layoutRight.addWidget(self.inputEmail)  # Add email field but it's hidden initially

        # creating buttons for login and register
        self.loginButton = QPushButton(text="Login", parent=self)
        self.loginButton.setStyleSheet("background-color: #E9E9E9; font-size: 15px; color: #000000; padding: 10px;")
        self.loginButton.setFixedWidth(150)
        self.loginButton.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.loginButton.clicked.connect(self.handle_auth)
        self.layoutRight.addWidget(self.loginButton)

        # Add "Switch to Register" button
        self.switchModeButton = QPushButton(text="Create Account", parent=self)
        self.switchModeButton.setStyleSheet(
            "background-color: transparent; font-size: 15px; color: #0000FF; padding: 5px; border: none;")
        self.switchModeButton.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.switchModeButton.clicked.connect(self.toggle_mode)
        self.layoutRight.addWidget(self.switchModeButton)

        # centering elements in the layout
        self.layoutRight.setAlignment(Qt.AlignCenter)
        self.layoutRight.setAlignment(self.loginLabel, Qt.AlignCenter)
        self.layoutRight.setAlignment(self.loginButton, Qt.AlignCenter)
        self.layoutRight.setAlignment(self.switchModeButton, Qt.AlignCenter)

        # setting up how the layouts will be constructed and the width of them
        mainLayout.addLayout(layoutLeft)
        mainLayout.addWidget(rightWidget)

        # first parameter is the layout (added in a mainLayout in order and second is the strech)
        mainLayout.setStretch(0, 1)  # Left layout
        mainLayout.setStretch(1, 1)  # Right layout

        self.setLayout(mainLayout)

    def toggle_mode(self):
        """Toggle between login and register modes"""
        try:
            self.is_login_mode = not self.is_login_mode

            # Update UI based on mode
            if self.is_login_mode:
                self.loginLabel.setText("LOGIN")
                self.loginButton.setText("Login")
                self.switchModeButton.setText("Create Account")
                self.inputEmail.setVisible(False)
            else:
                self.loginLabel.setText("REGISTER")
                self.loginButton.setText("Register")
                self.switchModeButton.setText("Back to Login")
                self.inputEmail.setVisible(True)

            # Clear fields
            self.inputUsername.clear()
            self.inputPassword.clear()
            self.inputEmail.clear()
        except Exception as e:
            print(f"Error toggling mode: {e}")

    def handle_auth(self):
        """Handle both login and registration based on current mode"""
        try:
            username = self.inputUsername.text()
            password = self.inputPassword.text()

            # Basic validation
            if not username or not password:
                self.login_system.show_message(
                    self,
                    "Error",
                    "Username and password are required",
                    QMessageBox.Warning
                )
                return

            if self.is_login_mode:
                # Handle login
                success, message = self.login_system.authenticate_user(username, password)
                if success:
                    # go to next page
                    self.stack.setCurrentIndex(1)
                else:
                    self.login_system.show_message(
                        self,
                        "Login Failed",
                        message,
                        QMessageBox.Warning
                    )
            else:
                # Handle registration
                email = self.inputEmail.text()
                success, message = self.login_system.register_user(username, password, email)
                if success:
                    self.login_system.show_message(
                        self,
                        "Registration Successful",
                        "Your account has been created. You can now log in."
                    )
                    # Switch back to login mode
                    self.toggle_mode()
                else:
                    self.login_system.show_message(
                        self,
                        "Registration Failed",
                        message,
                        QMessageBox.Warning
                    )
        except Exception as e:
            print(f"Authentication error: {e}")
            self.login_system.show_message(
                self,
                "Error",
                "An unexpected error occurred",
                QMessageBox.Critical
            )

    def login(self):
        """For backward compatibility with existing code"""
        self.handle_auth()

# this contains the GUI for the main page of our application
class MainPage(QWidget):
    def __init__(self, stack):
        super().__init__()

        self.stack = stack 

        self.fileSystem = FileSystem() # initializing the FileSystem 

        # setting the background color
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor('#DFDFDF'))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        self.setStyleSheet("QLabel{color: #000000;}") # setting the default text color for all labels

        # setting up the layout
        mainLayout = QVBoxLayout()

        # Creating the header bar at the top which will inclide the logo and buttons
        navBarWidget = QWidget()
        navBarWidget.setStyleSheet("background-color: #ffffff; border-radius: 10px; font-family: Arial; text-align: center;")  
        navBarWidget.setFixedHeight(150)
        navBarLayout = QHBoxLayout(navBarWidget)
        navBarLayout.setContentsMargins(50, 25, 50, 25)

        # Adding the logo and button
        logoImageLabel = QLabel(self)

        # Loading the image 
        logo = QPixmap("./images/pamLogo (1).png")  
        logoImageLabel.setPixmap(logo)

        # setting up the size
        logoImageLabel.setScaledContents(True)
        logoImageLabel.setFixedHeight(130)
        logoImageLabel.setFixedWidth(175)

        navBarLayout.addWidget(logoImageLabel)

        def createImageButton(image_path, text, click_action):
            """
            Creates a QPushButton with an icon above text while keeping a solid background.
            """
            # Create a QPushButton without text initially
            button = QPushButton()
            button.setFixedSize(150, 100)  # Set button size

            # Create a layout to stack icon and text
            layout = QVBoxLayout(button)
            layout.setSpacing(5)  # Space between icon and text
            layout.setAlignment(QtCore.Qt.AlignCenter)  # Center align content

            # Load the icon as a QLabel
            iconLabel = QLabel()
            iconPixmap = QPixmap(image_path).scaled(40, 40, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            iconLabel.setPixmap(iconPixmap)
            iconLabel.setAlignment(QtCore.Qt.AlignCenter)

            # Create a QLabel for the text
            textLabel = QLabel(text)
            textLabel.setAlignment(QtCore.Qt.AlignCenter)
            textLabel.setStyleSheet("font-size: 15px; color: #000000;")

            # Add widgets to layout
            layout.addWidget(iconLabel)
            layout.addWidget(textLabel)

            # Apply the layout to the button
            button.setLayout(layout)

            # Apply button styles
            button.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    border-radius: 8px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #E9E9E9;
                }
            """)

            # Connect the button action
            button.clicked.connect(click_action)

            return button

        # Create buttons with images
        summarizeButton = createImageButton("./images/summarize_icon.png", "Summarize", self.navigateSummarize)
        recordButton = createImageButton("./images/record_icon.png", "Record Meeting", self.navigateRecordAudio)

        # Add buttons to navbar
        navBarLayout.addWidget(summarizeButton)
        navBarLayout.addWidget(recordButton)

        # Creating a a gridview to display all summarized documents
        documentsWidget = QWidget()
        documentsWidget.setStyleSheet("background-color: #ffffff; border-radius: 10px; font-family: Arial;")  

        self.documentsLayout = QGridLayout(documentsWidget)
        self.documentsLayout.setContentsMargins(50, 25, 50, 25)
        self.documentsLayout.setSpacing(20)
        
        # adding in the gridlayout for the documents
        self.updateDocuments()

        # adding the layouts to the mainLayout
        mainLayout.addWidget(navBarWidget) 
        mainLayout.addWidget(documentsWidget) 

        # setting the layout to the window
        self.setLayout(mainLayout)

    # go to summarize page
    def navigateSummarize(self):
        sumPage = self.stack.widget(2)
        sumPage.resetFileInput() # rest the summarization page
        self.stack.setCurrentIndex(2)

    # go to record audio page
    def navigateRecordAudio(self):
        recordAudioPage = self.stack.widget(3)
        self.stack.setCurrentIndex(3)

    # go to document page
    def navigateDocument(self, fileName):
        # Send the file name to the DocumentPage
        self.docPage = DocumentPage(self.stack, fileName)
        
        # Adding the DocumentPage to the stack and switching to it
        self.stack.addWidget(self.docPage)
        self.stack.setCurrentWidget(self.docPage)

    # updating the gridlayout when something has changed
    def updateDocuments(self):

        # displaying the files that exist in the directory of summarized notes
        self.fileSystem.searchDirectory()
        fileAmt = self.fileSystem.fileAmt

        row = 0  # variable initialized represents the rows in the grid
        while fileAmt > 0:

            for col in range(0, 5):

                # only run this code if file size is in range
                if fileAmt >= 5 or col < fileAmt:

                    # Get file name first
                    fileIndex = (row * 5) + col
                    fileName = self.fileSystem.fileNames[fileIndex]

                    # Grey box (container for the file button)
                    documentGridWidget = QWidget()
                    documentGridWidget.setFixedHeight(250)
                    documentGridWidget.setFixedWidth(175)
                    documentGridWidget.setStyleSheet("""
                        QWidget {
                            background-color: #868686; 
                            border-radius: 10px; 
                            font-family: Arial; 
                            color: #000000;
                        }
                        QWidget:hover {
                            background-color: #777777;
                        }
                    """)

                    # Setting up the layout for a document and its title
                    documentGrid = QVBoxLayout(documentGridWidget)
                    documentGrid.setContentsMargins(10, 10, 10, 10)  # Keeps spacing for the inner button
                    documentGrid.setSpacing(5)

                    # Blue rectangle (representing document)
                    documentButton = QPushButton("", parent=documentGridWidget)
                    documentButton.setStyleSheet("""
                        QPushButton {
                            background-color: #CAECF0;
                            border-radius: 5px;
                        }
                        QPushButton:hover {
                            background-color: #B5DDE0;
                        }
                    """)
                    documentButton.setFixedHeight(150)
                    documentButton.setFixedWidth(100)
                    documentButton.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
                    
                    # Add onclick to the blue button as well
                    documentButton.clicked.connect(lambda checked=False, name=fileName: self.navigateDocument(name))

                    # Filename label
                    fileNameLabel = QLabel(fileName)
                    fileNameLabel.setAlignment(Qt.AlignCenter)
                    fileNameLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                    fileNameLabel.setFixedWidth(155)
                    
                    # Apply proper padding and prevent overflow
                    fileNameLabel.setStyleSheet("""
                        font-size: 14px; 
                        font-weight: bold;
                        color: #000000;
                        background-color: transparent;
                        padding: 5px;
                        min-width: 155px;
                        max-width: 155px;
                    """)

                    # Ensure elided text is calculated correctly per QLabel
                    def updateElidedText(label, fullText):
                        available_width = label.width() - 20  # Subtract padding for correct fitting

                        # Only apply elision when width is available
                        if available_width > 0:
                            metrics = QFontMetrics(label.font())
                            elidedText = metrics.elidedText(fullText, Qt.ElideRight, available_width)
                            label.setText(elidedText)

                    # Call the function per label and ensure updates on resize
                    updateElidedText(fileNameLabel, fileName)
                    fileNameLabel.resizeEvent = lambda event, lbl=fileNameLabel, text=fileName: updateElidedText(lbl, text)

                    # Add elements to the layout
                    documentGrid.addWidget(documentButton, alignment=Qt.AlignCenter)
                    documentGrid.addWidget(fileNameLabel, alignment=Qt.AlignCenter)

                    # Keep the click event for the entire grey box
                    documentGridWidget.mousePressEvent = lambda event, name=fileName: self.navigateDocument(name)

                    # Add widget to the grid layout
                    self.documentsLayout.addWidget(documentGridWidget, row, col)

                else:
                    break 
            row += 1  # Moving to the next row
            fileAmt -= 5  # Removing files that have been displayed

# this contains the GUI for the main page of our application
class RecordAudioPage(QWidget):

    record = False;

    def __init__(self, stack):
        super().__init__()

        self.stack = stack

        # setting the background color
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor('#DFDFDF'))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # setting up the layout
        mainLayout = QVBoxLayout()

        # this is the nav bar that contains the logo and a back button
        navBarWidget = QWidget()
        navBarWidget.setStyleSheet("background-color: #ffffff; border-radius: 10px; font-family: Arial; text-align: center;")
        navBarWidget.setFixedHeight(150)
        navBarLayout = QHBoxLayout(navBarWidget)
        navBarLayout.setContentsMargins(50, 25, 50, 25)

        backButton = QPushButton(text="Back", parent=self)
        backButton.setStyleSheet("background-color: #E9E9E9; font-size: 15px; color: #000000; padding: 10px;")
        backButton.setFixedWidth(150)
        backButton.setGraphicsEffect(shadow)
        backButton.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        backButton.clicked.connect(self.navigateHome)
        navBarLayout.addWidget(backButton)

        # Adding the logo and button
        logoImageLabel = QLabel(self)

        # Loading the image 
        logo = QPixmap("./images/pamLogo.png")  
        logoImageLabel.setPixmap(logo)

        # setting up the size
        logoImageLabel.setScaledContents(True)
        logoImageLabel.setFixedHeight(150)
        logoImageLabel.setFixedWidth(150)

        navBarLayout.addWidget(logoImageLabel)

        # adding the components to the mainLayout
        mainLayout.addWidget(navBarWidget)

        # adding only a record button
        recordButton = QPushButton(text="Record", parent=self)
        recordButton.setStyleSheet("background-color: #E9E9E9; font-size: 15px; color: #000000; padding: 10px;")
        recordButton.setFixedWidth(150)
        recordButton.setGraphicsEffect(shadow)
        recordButton.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        recordButton.clicked.connect(self.recordAudio)

        mainLayout.addWidget(recordButton)
        
        # # algining the widgets
        # mainLayout.setAlignment(self.dropBox, Qt.AlignCenter)
        # mainLayout.setAlignment(self.summarizeButton, Qt.AlignCenter)

        # setting the layout to the window
        self.setLayout(mainLayout)


    # go to summarize page
    def recordAudio(self):
        Recorder.recordAudio()
        filename = speakerDiarization.transcribeAndDiarize()
        pam.summarize(filename)

        # going back to the main page
        mainPage = self.stack.widget(1)
        mainPage.updateDocuments()

    # this function navigates back to the main page
    def navigateHome(self):
        self.stack.setCurrentIndex(1)


# this contains the GUI for summarizing a note
class SummarizationPage(QWidget):
    def __init__(self, stack):
        super().__init__()

        self.stack = stack

        # setting the background color
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor('#DFDFDF'))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # setting up the layout
        mainLayout = QVBoxLayout()

        # this is the nav bar that contains the logo and a back button
        navBarWidget = QWidget()
        navBarWidget.setStyleSheet("background-color: #ffffff; border-radius: 10px; font-family: Arial; text-align: center;")
        navBarWidget.setFixedHeight(150)
        navBarLayout = QHBoxLayout(navBarWidget)
        navBarLayout.setContentsMargins(50, 25, 50, 25)

        backButton = QPushButton(text="Back", parent=self)
        backButton.setStyleSheet("background-color: #E9E9E9; font-size: 15px; color: #000000; padding: 10px;")
        backButton.setFixedWidth(150)
        backButton.setGraphicsEffect(shadow)
        backButton.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        backButton.clicked.connect(self.navigateHome)
        navBarLayout.addWidget(backButton)

        # Adding the logo and button
        logoImageLabel = QLabel(self)

        # Loading the image 
        logo = QPixmap("./images/pamLogo.png")  
        logoImageLabel.setPixmap(logo)

        # setting up the size
        logoImageLabel.setScaledContents(True)
        logoImageLabel.setFixedHeight(150)
        logoImageLabel.setFixedWidth(150)

        navBarLayout.addWidget(logoImageLabel)

        self.resetFileInput()

        # adding the components to the mainLayout
        mainLayout.addWidget(navBarWidget) 
        mainLayout.addWidget(self.dropBox)
        mainLayout.addWidget(self.summarizeButton)
        
        # algining the widgets
        mainLayout.setAlignment(self.dropBox, Qt.AlignCenter)
        mainLayout.setAlignment(self.summarizeButton, Qt.AlignCenter)

        # setting the layout to the window
        self.setLayout(mainLayout)

    # built in function for drop events
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    # built in function for drop events
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    # This function is a built in function to react to a drop event
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            fileName = event.mimeData().urls()[0].toLocalFile()
            event.setDropAction(Qt.CopyAction)
            self.dropBox.setText(fileName.split('/')[-1])

    # This function will invoke the summarization component
    def summarize(self,filename):
        pam.summarize(filename)
        mainPage = self.stack.widget(1)
        mainPage.updateDocuments() # update the main page to reflect the files in the directory
        self.stack.setCurrentIndex(1)

    # this function navigates back to the main page
    def navigateHome(self):
        self.stack.setCurrentIndex(1)

    # this will reset the file input for the drop box
    def resetFileInput(self):
        # if the drop box has already been created than we reset the text
        if hasattr(self, 'dropBox'):
            self.dropBox.setText("Drop File Here")
        else:
            # creating a label where the user can drag and drop files to summarize
            self.setAcceptDrops(True) # allows drags and drops
            self.dropBox = QLabel("Drop File Here", self)
            self.dropBox.setWordWrap(True)
            self.dropBox.setStyleSheet("border: 3px dashed #000000; font-size: 20px;")
            self.dropBox.setAlignment(Qt.AlignCenter)
            self.dropBox.setFixedHeight(300)
            self.dropBox.setFixedWidth(300)

            # Creating a button for summarizing
            self.summarizeButton = QPushButton(text="Summarize", parent=self)
            self.summarizeButton.setStyleSheet("background-color: #E9E9E9; font-size: 15px; color: #000000; padding: 10px;")
            self.summarizeButton.setFixedWidth(150)
            self.summarizeButton.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
            # summarizeButton.setGraphicsEffect(shadow)
            self.summarizeButton.clicked.connect(lambda: self.summarize(self.dropBox.text()))

# this contains the GUI for opening up a document
class DocumentPage(QWidget):

    def __init__(self, stack, fileName = None):
        super().__init__()

        self.stack = stack
        self.fileName = fileName

        fileSystem = FileSystem() # initializing the file system

        # font for titles
        titleFont = QFont()
        titleFont.setFamily("Times New Roman")   
        titleFont.setPointSize(20)     
        titleFont.setBold(True)   

        headingFont = QFont()
        headingFont.setFamily("Times New Roman")   
        headingFont.setPointSize(16)     

        paragraphFont = QFont()
        paragraphFont.setFamily("Times New Roman")   
        paragraphFont.setPointSize(11)     

        # setting the background color
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor('#DFDFDF'))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # setting up the layout
        mainLayout = QVBoxLayout()

        # ----------------------------- Navbar START ----------------------------- #
        navBarWidget = QWidget()
        navBarWidget.setStyleSheet("background-color: #ffffff; border-radius: 10px; font-family: Arial; text-align: center;")
        navBarWidget.setFixedHeight(100)

        # Set up the layout for the navbar
        navBarLayout = QHBoxLayout(navBarWidget)
        navBarLayout.setContentsMargins(0, 0, 0, 0)
        navBarLayout.setSpacing(0)

        # Back Button (Top Left)
        backButtonContainer = QVBoxLayout()
        backButtonContainer.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        backButtonContainer.setContentsMargins(10, 10, 0, 0)

        backButton = QPushButton(parent=self)
        backButton.setFixedSize(75, 75)
        backButton.setStyleSheet("""
            QPushButton {
                background-color: #E9E9E9; 
                font-size: 20px; 
                color: #000000; 
            }
            QPushButton:hover {
                background-color: #D6D6D6;
            }
        """)
        backButton.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        backButton.setText("←")
        backButton.setGraphicsEffect(shadow)
        backButton.clicked.connect(self.navigateHome)

        backButtonContainer.addWidget(backButton)
        navBarLayout.addLayout(backButtonContainer)

        # Add left spacer
        navBarLayout.addStretch(1)

        # Add the logo (Centered)
        logoImageLabel = QLabel(self)
        logo = QPixmap("./images/pamLogo (1).png")  
        logoImageLabel.setPixmap(logo)
        logoImageLabel.setScaledContents(True)
        logoImageLabel.setFixedHeight(125)
        logoImageLabel.setFixedWidth(150)
        navBarLayout.addWidget(logoImageLabel, alignment=QtCore.Qt.AlignCenter)

        # Add right spacer
        navBarLayout.addStretch(1)

        # Invisible Empty Widget to match Back Button size
        emptyWidget = QWidget()
        emptyWidget.setFixedSize(85, 85)
        navBarLayout.addWidget(emptyWidget)
        # ----------------------------- Navbar END ----------------------------- #

        # ----------------------------- File Specifications Bar ----------------------------- #
        fileSpecWidget = QWidget()
        fileSpecWidget.setStyleSheet("""
            background-color: #ffffff;
            border-radius: 10px;
            font-family: Arial;
            color: #000000;
            margin-top: 10px;
            margin-bottom: 10px;
            background-color: #D1D6D7;
        """)
        fileSpecWidget.setFixedHeight(100)
        
        fileSpecLayout = QHBoxLayout(fileSpecWidget)
        
        # File name
        fileNameLabel = QLabel(f"File: {fileName}")
        fileNameLabel.setFont(QFont("Times New Roman", 12))
        fileSpecLayout.addWidget(fileNameLabel)
        
        # Add spacer between file name and file size
        fileSpecLayout.addStretch(1)
        
        # File size
        try:
            fileSize = fileSystem.getSize(fileName)
            fileSizeLabel = QLabel(f"Size: {fileSize}")
            fileSizeLabel.setFont(QFont("Times New Roman", 12))
            fileSpecLayout.addWidget(fileSizeLabel)
        except Exception as e:
            print(f"Error getting file size: {str(e)}")
        
        # ----------------------------- Document Content ----------------------------- #
        
        # Creating a content widget
        contentWidget = QWidget()
        contentWidget.setStyleSheet("""
            background-color: #ffffff;
            border-radius: 10px;
            font-family: Arial;
            color: #000000;
            padding: 20px;
        """)
        
        documentLayout = QVBoxLayout(contentWidget)
        documentLayout.setSpacing(15)
        
        try:
            print(f"Loading document: {fileName}")

            # Get sections from the document
            sections = fileSystem.getHeadingsAndContent(fileName)
            
            print(f"Found {len(sections)} sections")
            
            # If sections were found, display them
            if sections and len(sections) > 0:
                for heading, content in sections:
                    # Create heading label with the section title
                    headingLabel = QLabel(heading)
                    headingLabel.setFont(headingFont)
                    headingLabel.setStyleSheet("color: #000000; font-weight: bold;")
                    headingLabel.setWordWrap(True)
                    documentLayout.addWidget(headingLabel)
                    
                    # Create content label with proper formatting
                    contentLabel = QLabel()
                    contentLabel.setFont(paragraphFont)
                    contentLabel.setStyleSheet("color: #000000;")
                    contentLabel.setWordWrap(True)
                    
                    # Format bullet points properly if present
                    if "-" in content:
                        formatted_content = ""
                        for line in content.split("\n"):
                            if line.strip().startswith("-"):
                                formatted_content += f"• {line.strip()[1:].strip()}<br>"
                            else:
                                formatted_content += f"{line}<br>"
                        contentLabel.setText(formatted_content)
                    else:
                        contentLabel.setText(content)
                    
                    documentLayout.addWidget(contentLabel)
                    documentLayout.addSpacing(20)  # Add space between sections
            else:
                # If no sections were found
                noContentLabel = QLabel("No content available in this document")
                noContentLabel.setFont(paragraphFont)
                noContentLabel.setAlignment(Qt.AlignCenter)
                documentLayout.addWidget(noContentLabel)
                
        except Exception as e:
            print(f"Error loading document: {str(e)}")
            errorLabel = QLabel(f"Error: {str(e)}")
            errorLabel.setFont(paragraphFont)
            errorLabel.setAlignment(Qt.AlignCenter)
            documentLayout.addWidget(errorLabel)

        # Create a scroll area and set the content widget to it
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setFrameShape(QFrame.NoFrame)
        scrollArea.setStyleSheet("""
            QScrollArea {
                border: none;
                border-radius: 10px;
                background-color: #ffffff;
            }

            QScrollArea > QWidget {
                border-radius: 10px;
                background-color: #ffffff;
            }

            /* Scrollbar Styling */
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 10px;
                margin: 2px 5px 2px 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 0, 0, 0.2);
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
                border: none;
            }
        """)
        
        # Set the content widget to the scroll area
        scrollArea.setWidget(contentWidget)

        # Adding the widgets to the mainLayout
        mainLayout.addWidget(navBarWidget)
        mainLayout.addWidget(fileSpecWidget)
        mainLayout.addWidget(scrollArea)
        
        # Setting the main layout to the window
        self.setLayout(mainLayout)

    # this function navigates back to the main page
    def navigateHome(self):
        self.stack.setCurrentIndex(1)

# this class manages the stacked pages
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # The QStackedLayout will store all the different QWidgets/pages
        self.stack = QStackedWidget()
        
        # storing all the pages to the stack
        self.loginPage = LoginWindow(self.stack)
        self.mainPage = MainPage(self.stack)
        self.summarizationPage = SummarizationPage(self.stack)
        self.recordAudioPage = RecordAudioPage(self.stack)

        # The way the pages are added to the stack determine thier index
        self.stack.addWidget(self.loginPage) # 0
        self.stack.addWidget(self.mainPage) # 1
        self.stack.addWidget(self.summarizationPage) # 2
        self.stack.addWidget(self.recordAudioPage) # 2


        # Set the stacked widget as the central widget of QMainWindow
        self.setCentralWidget(self.stack)

        # setting up the default size of the browser
        self.setMinimumSize(800, 600)

# config setup for Qapplication
app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec_())