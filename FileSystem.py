# File Name: Minutes.py
# Authors: Javier Chung, Andy Dai, Antonio Lio, Jason Stuckless
# Description: Functionality for reading files in a directory

import os
import shutil
import docx2txt 
import re 


class FileSystem:

    def __init__(self, fileDirectory = "./MeetingNotes"):
        self.fileNames = []
        self.fileAmt = 0
        self.fileDirectory = fileDirectory
        self.sectionHeadings = ["Opening", "Present", "Absent", "Agenda Approval", "Previous Meeting Approval",
                   "Previous Meeting Summary", "Summary of Meeting", "Adjournment"]


    # this method searches for the amount of files wihtin the directory while populating a list with thier names
    def searchDirectory(self):

        # resetting the values
        self.fileNames = []
        self.fileAmt = 0

        # this views all the files and stores the path name of them in an array
        for f in os.listdir(self.fileDirectory):
            filepath = os.path.join(self.fileDirectory, f) # checking the files in the directory

            if (os.path.isfile(filepath) and f.endswith(".docx")): # finding .docx files and non corrupt files

                self.fileNames.append(f)
                self.fileAmt = self.fileAmt + 1

    # this method returns the file size
    def getSize(self, fileName):
        size = os.path.getsize(self.fileDirectory + "/" + fileName)
        return (str(size) + " bytes") 

    # this method move sthe file to a specified location
    def moveFile(self, fileName):
        destinationFilePath = os.path.join(self.fileDirectory, fileName)
        shutil.move( (fileName), destinationFilePath) 

    # this method returs a list of actionable items after opening a file
    def getActionableItemsList(self, fileName):
        actionableItemsList = []

        destinationFilePath = os.path.join(self.fileDirectory, fileName)


        # opening the file
        with open(destinationFilePath, 'r') as f:
            for line in f:
                actionableItemsList.append(line.strip())

        return actionableItemsList

    def getHeadingsAndContent(self, fileName):
        sectionContent = []
        destinationFilePath = os.path.join(self.fileDirectory, fileName)
        minutesDoc = docx2txt.process(destinationFilePath) # reading the document


        # matches a number (d) and . with any text behind it untill a new line
        # the (.*?) gets the content up untill the next number and .
        headings = r"(\d+\.\s+[^\n]+)(.*?)(?=\n\d+\.\s|$)" 

        # finds all headings and partitions them with the content associated with it and puts it in a dynamic list
        return re.findall(headings, minutesDoc, re.DOTALL)
