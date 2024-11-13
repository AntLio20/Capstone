# File Name: Minutes.py
# Authors: Javier Chung, Andy Dai, Antonio Lio, Jason Stuckless
# Description: Functionality for reading files in a directory

import os

# initializing variables
fileDirectory = "./MeetingNotes"
fileNames = []
fileAmt = 0

# this views all the files and stores the path name of them in an array
for f in os.listdir(fileDirectory):
    if (os.path.isfile(f)):
        fileNames.append(f)
        fileAmt = fileAmt + 1
