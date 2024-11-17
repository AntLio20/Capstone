# File Name: pam.py
# Authors: Javier Chung, Andy Dai, Antonio Lio, Jason Stuckless
# Date: Oct 26, 2024
# Description: This is the main page containing the GUI

# pip3 install pyqt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QStackedWidget, QPushButton, QVBoxLayout, QLineEdit, QLabel, QHBoxLayout, QGraphicsDropShadowEffect, QGridLayout, QScrollArea
from PyQt5.QtGui import QDragEnterEvent, QDragLeaveEvent, QDragMoveEvent, QDropEvent, QPalette, QColor, QFont, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal

import sys
from FileSystem import FileSystem
import pam


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

        # Setting the background color of the page
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor('#DFDFDF'))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        self.setStyleSheet("QLabel{color: #000000;}") # setting the default text color for all labels

        # Adding content onto the gui page
        mainLayout = QHBoxLayout() # setting main layout to be horizontal

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
        rightWidget.setStyleSheet("background-color: #ffffff; border-radius: 10px; font-family: Arial; text-align: center;")  

        rightWidget.setGraphicsEffect(shadow)

        # Setting up the layout on the right side to be vertical
        layoutRight = QVBoxLayout(rightWidget)
        layoutRight.setContentsMargins(50, 25, 50, 25)
        layoutRight.setSpacing(20)

        loginLabel = QLabel("LOGIN")
        loginFont = QFont("Arial", 40, QFont.Bold)
        loginLabel.setFont(loginFont)
        layoutRight.addWidget(loginLabel)

        # Setting up input on the GUI
        self.inputUsername = QLineEdit() # Variable can be used anywhere in class when self is in the front
        self.inputPassword = QLineEdit()

        # styling for the inputs
        inputStyle = "background-color: #E8E8E8; color: #7A7A7A; padding: 10px; font-size: 20px;"
        self.inputUsername.setStyleSheet(inputStyle)
        self.inputPassword.setStyleSheet(inputStyle)

        # Setting up placeholder text
        self.inputUsername.setPlaceholderText("Username")
        self.inputPassword.setPlaceholderText("Password")

        # adding input for the username and password to the layout
        layoutRight.addWidget(self.inputUsername) 
        layoutRight.addWidget(self.inputPassword) 

        # creating a button with a text and parent widget
        loginButton = QPushButton(text="Login", parent=self)
        loginButton.setStyleSheet("background-color: #E9E9E9; font-size: 15px; color: #000000; padding: 10px;")
        loginButton.setFixedWidth(150)
        loginButton.clicked.connect(self.login)
        layoutRight.addWidget(loginButton) # adding a button

        # centering elements in the layout
        layoutRight.setAlignment(Qt.AlignCenter)
        layoutRight.setAlignment(loginLabel, Qt.AlignCenter)
        layoutRight.setAlignment(loginButton, Qt.AlignCenter)

        # setting up how the layouts will be constructed and the width of them
        mainLayout.addLayout(layoutLeft) 
        mainLayout.addWidget(rightWidget)

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

        summarizeButton = QPushButton(text="Summarize", parent=self)
        summarizeButton.setStyleSheet("background-color: #E9E9E9; font-size: 15px; color: #000000; padding: 10px;")
        summarizeButton.setFixedWidth(150)
        summarizeButton.clicked.connect(self.navigateSummarize)
        navBarLayout.addWidget(summarizeButton)

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
        self.stack.setCurrentIndex(2)

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
                if(col <= fileAmt):

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
                    documentGrid.addWidget(documentButton)
                    documentGrid.setAlignment(documentButton, Qt.AlignCenter)
            
                    # displaying the file name
                    fileIndex = (row * 5) + col # getting the file index
                    fileName = self.fileSystem.fileNames[fileIndex]
                    fileNameLabel = QLabel(fileName)
                    documentButton.clicked.connect( # connecting the button to a function
                        # by using lambda, we allow the navigation to be only executed on when the button is clicked
                        lambda _, name=fileName: self.navigateDocument(name)
                        )
                    documentGrid.addWidget(fileNameLabel)
                    documentGrid.setAlignment(fileNameLabel, Qt.AlignCenter)

                    fileAmt = fileAmt - 1 # updating the file amount that is not displayed

                    # adding the visualy represented file to the gridlayout
                    self.documentsLayout.addWidget(documentGridWidget, row, col)
                else:
                    break 
            row = row + 1

        
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

        # creating a label where the user can drag and drop files to summarize
        self.setAcceptDrops(True) # allows drags and drops
        self.dropBox = QLabel("Drop File Here", self)
        self.dropBox.setStyleSheet("border: 3px dashed #000000; font-size: 20px;")
        self.dropBox.setAlignment(Qt.AlignCenter)
        self.dropBox.setFixedHeight(300)
        self.dropBox.setFixedWidth(300)

        # Creating a button for summarizing
        summarizeButton = QPushButton(text="Summarize", parent=self)
        summarizeButton.setStyleSheet("background-color: #E9E9E9; font-size: 15px; color: #000000; padding: 10px;")
        summarizeButton.setFixedWidth(150)
        # summarizeButton.setGraphicsEffect(shadow)
        summarizeButton.clicked.connect(lambda: self.summarize( self.dropBox.text()))

        # adding the components to the mainLayout
        mainLayout.addWidget(navBarWidget) 
        mainLayout.addWidget(self.dropBox)
        mainLayout.addWidget(summarizeButton)
        
        # algining the widgets
        mainLayout.setAlignment(self.dropBox, Qt.AlignCenter)
        mainLayout.setAlignment(summarizeButton, Qt.AlignCenter)

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
            filepath = event.mimeData().urls()[0].toLocalFile()
            fileName = filepath.split('/')[-1] # splitting the file path by '/' and getting the last element
            event.setDropAction(Qt.CopyAction)
            self.dropBox.setText(fileName)

    # This function will invoke the summarization component
    def summarize(self,filename):
        pam.summarize(filename)
        mainPage = self.stack.widget(1)
        mainPage.updateDocuments() # update the main page to reflect the files in the directory
        self.stack.setCurrentIndex(1)

    # this function navigates back to the main page
    def navigateHome(self):
        self.stack.setCurrentIndex(1)


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

        # The way the pages are added to the stack determine thier index
        self.stack.addWidget(self.loginPage) # 0
        self.stack.addWidget(self.mainPage) # 1
        self.stack.addWidget(self.summarizationPage) # 2

        # Set the stacked widget as the central widget of QMainWindow
        self.setCentralWidget(self.stack)

        # setting up the default size of the browser
        self.setMinimumSize(800, 600)

# config setup for Qapplication
app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec_())







