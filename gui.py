# File Name: pam.py
# Authors: Javier Chung, Andy Dai, Antonio Lio, Jason Stuckless
# Date: Oct 26, 2024
# Description: This is the main page containing the GUI

# pip install PyQt5
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QStackedWidget, QPushButton, QVBoxLayout, QLineEdit, QLabel, QHBoxLayout, QGraphicsDropShadowEffect, QGridLayout, QScrollArea
from PyQt5.QtGui import QDragEnterEvent, QDragLeaveEvent, QDragMoveEvent, QDropEvent, QPalette, QColor, QFont, QPixmap, QCursor
from PyQt5.QtCore import Qt, pyqtSignal
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

        # Creating the header bar at the top which will inclide the logo and button to summarzie a transcript
        navBarWidget = QWidget()
        navBarWidget.setStyleSheet("background-color: #ffffff; border-radius: 10px; font-family: Arial; text-align: center;")  
        navBarWidget.setFixedHeight(150)
        navBarLayout = QHBoxLayout(navBarWidget)
        navBarLayout.setContentsMargins(50, 25, 50, 25)

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

        # adding a summarize button
        summarizeButton = QPushButton(text="Summarize", parent=self)
        summarizeButton.setStyleSheet("background-color: #E9E9E9; font-size: 15px; color: #000000; padding: 10px;")
        summarizeButton.setFixedWidth(150)
        summarizeButton.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        summarizeButton.clicked.connect(self.navigateSummarize)
        navBarLayout.addWidget(summarizeButton)

        # adding a buttong to take the user to the record audio page
        recordButton = QPushButton(text="Record Meeting", parent=self)
        recordButton.setStyleSheet("background-color: #E9E9E9; font-size: 15px; color: #000000; padding: 10px;")
        recordButton.setFixedWidth(150)
        recordButton.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        recordButton.clicked.connect(self.navigateRecordAudio)
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


    # updating the gridlayout whenn something has been changed
    def updateDocuments(self):

        # displaying the files that exist in the directory of summarized notes
        self.fileSystem.searchDirectory()
        fileAmt = self.fileSystem.fileAmt

        row = 0; # variable intialized represents the rows in the grid
        while (fileAmt > 0):

            for col in range(0,5):

                # only running this code the file size is in range
                if(fileAmt >= 5 or col < fileAmt ):

                    # formatting the size of one grid and setting the styling
                    documentGridWidget = QWidget()
                    documentGridWidget.setFixedHeight(250)
                    documentGridWidget.setFixedWidth(175)
                    documentGridWidget.setStyleSheet("background-color: #868686; border-radius: 10px; font-family: Arial; color: #000000;")

                    # setting up the layout for a document and its title
                    documentGrid = QVBoxLayout(documentGridWidget)

                    # display a visual of a document using a button
                    documentButton = QPushButton(text="", parent = self)
                    documentButton.setStyleSheet("background-color: #CAECF0; border-radius: 0px;")
                    documentButton.setFixedHeight(150)
                    documentButton.setFixedWidth(100)
                    documentButton.setGraphicsEffect(shadow)
                    documentButton.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
                    documentGrid.addWidget(documentButton)
                    documentGrid.setAlignment(documentButton, Qt.AlignCenter)
            
                    # displaying the file name
                    fileIndex = (row * 5) + col # getting the file index

                    print("File Index: " + str(fileIndex))

                    fileName = self.fileSystem.fileNames[fileIndex]
                    fileNameLabel = QLabel(fileName)
                    documentButton.clicked.connect( # connecting the button to a function
                        # by using lambda, we allow the navigation to be executed when the button is clicked
                        lambda _, name=fileName: self.navigateDocument(name)
                        )
                    documentGrid.addWidget(fileNameLabel)
                    documentGrid.setAlignment(fileNameLabel, Qt.AlignCenter)                        

                    # adding the visualy represented file to the gridlayout
                    self.documentsLayout.addWidget(documentGridWidget, row, col)
                else:
                    break 
            row = row + 1 # Moving to the next row
            fileAmt = fileAmt - 5 # Removing files that have been displayed

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
       
        # Setting up the left and right layout that will be containing the document infor
        documentLayout = QHBoxLayout()

        # setting up the Left layout which will contain the File Specifications and Actionable Items --------------------------
        leftWidget = QWidget()
        leftWidget.setStyleSheet(" border-radius: 10px; font-family: Arial; text-align: center;")
        leftLayout = QVBoxLayout(leftWidget)

        # setting up the file info
        fileInfoWidget = QWidget()
        fileInfoWidget.setStyleSheet("background-color: #ffffff; text-align: center; color: #000000")
        fileInfoLayout = QVBoxLayout(fileInfoWidget)

        # adding the title
        fileDescriptionTitle = QLabel("File Specifications")
        fileDescriptionTitle.setFont(titleFont)
        fileInfoLayout.addWidget(fileDescriptionTitle)

        # adding the Labels for the file descriptors
        fileNameLabel = QLabel("File name: " + fileName)
        fileSizeLabel = QLabel("File size: " + fileSystem.getSize(fileName))
        fileInfoLayout.addWidget(fileNameLabel)
        fileInfoLayout.addWidget(fileSizeLabel)

        # actionable items setup
        actionableItemsWidget = QWidget()
        actionableItemsWidget.setStyleSheet("background-color: #ffffff; text-align: center; color: #000000;")
        actionableItemsLayout = QVBoxLayout(actionableItemsWidget)

        # adding the title
        actionableItemsTitle = QLabel("Actiontable Items")
        actionableItemsTitle.setFont(titleFont)
        actionableItemsLayout.addWidget(actionableItemsTitle)

        # opening the ActioanableItems txt file
        actionableItems = []
        actionableItemFile = fileName.replace("minutes.docx", "actions.txt")
        actionableItems = fileSystem.getActionableItemsList(actionableItemFile)

        # adding labels onto the actionable items list
        for item in actionableItems:
            itemLabel = QLabel(item)
            itemLabel.setWordWrap(True)
            actionableItemsLayout.addWidget(itemLabel)

        # adding the sections into the left layout
        leftLayout.addWidget(fileInfoWidget)
        leftLayout.addWidget(actionableItemsWidget)

        # -------------------------------------------------------------------------------------

        # ------------------------------ Right Layout START ----------------------------------#

        # creating an area for scrolling
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)

        rightWidget = QWidget();
        rightWidget.setStyleSheet("background-color: #ffffff; border-radius: 10px; font-family: Arial; text-align: center; color: #000000;")
        rightLayout = QVBoxLayout(rightWidget)

        sectionHeadings = fileSystem.sectionHeadings
        sections = fileSystem.getHeadingsAndContent(fileName)

        for i in range (0, len(sectionHeadings)):
            headingLabel = QLabel(sections[i][0])
            headingLabel.setWordWrap(True)
            headingLabel.setFont(headingFont)

            contentLabel = QLabel(sections[i][1])
            contentLabel.setWordWrap(True)
            contentLabel.setFont(paragraphFont)

            # adding the heading and content 
            rightLayout.addWidget(headingLabel)
            rightLayout.addWidget(contentLabel)

        # adding the scroll area to the right widget
        scrollArea.setWidget(rightWidget)
        # ------------------------------ Right Layout END ----------------------------------#

        # adding the left and right layout to the document layout
        documentLayout.addWidget(leftWidget)
        documentLayout.addWidget(scrollArea)
        documentLayout.setStretch(0, 2)  # Left layout
        documentLayout.setStretch(1, 3)  # Right layout

        # adding the widgets/ layouts to the mainLayout
        mainLayout.addWidget(navBarWidget) 
        mainLayout.addLayout(documentLayout)
        
        # setting the layout to the window
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
