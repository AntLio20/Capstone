import os
import time
import docx2txt

# Clean up transcript, timestamp/speaker = 0 to remove
def cleanTranscript (transcript, timestamp, speaker):
    # split each line of text into list
    splitTranscript = transcript.splitlines(keepends=True)

    # check modes and perform corresponding list item deletions
    if (timestamp == 0) and (speaker == 0):
        del splitTranscript[0::4]
        del splitTranscript[0::3]
    elif (timestamp == 0) and (speaker == 1):
        del splitTranscript[0::4]
    elif (timestamp == 1) and (speaker == 0):
        del splitTranscript[1::4]

    # return text to string format and return it
    text = ""
    for line in splitTranscript:
        if line != '\n':
            text += line
    return text

# Obtain the duration of a meeting
def meetingDuration (filepath):
    transcript = docx2txt.process(filepath)
    subString = ''
    subString2 = ''
    for c in reversed(transcript):
        if c == '>':
            break
        subString += c
    for c in reversed(subString):
        subString2 += c
    subString = subString2[1:]
    if subString[1] == ":":
        durationHours = int(subString[0])
        durationMinutes = int(subString[2:4])
    else:
        durationHours = int(subString[0:2])
        durationMinutes = int(subString[3:5])
    return durationHours, durationMinutes

# Calculate meeting start time using raw file date minus meeting duration
def calculateStart (filepath):
    rawDate = time.ctime(os.path.getctime(filepath))
    duration = meetingDuration(filepath)
    if rawDate[9].isspace():
        rawHours = int(rawDate[10:12])
        rawMinutes = int(rawDate[13:15])
    else:
        rawHours = int(rawDate[11:13])
        rawMinutes = int(rawDate[14:16])
    minutes = rawMinutes - duration[1]
    if minutes < 0:
        minutes += 60
        hours = rawHours - duration[0] - 1
    else:
        hours = rawHours - duration[0]
    return hours, minutes

# Obtain formal form of creation date of transcript file and meeting start time
def extractFormalDate (filepath):
    rawDate = time.ctime(os.path.getctime(filepath))
    startTime = calculateStart(filepath)
    if rawDate[9].isspace():
        date = Date(rawDate[:3], rawDate[4:7], rawDate[8], startTime[0], startTime[1], "", rawDate[19:23])
    else:
        date = Date(rawDate[:3], rawDate[4:7], rawDate[8:10], startTime[0], startTime[1], "", rawDate[20:24])
    return date

# Obtain file date for use in file naming convention
def extractFilenameDate (filepath):
    rawDate = time.ctime(os.path.getctime(filepath))
    date = rawDate[-4:] + "-"
    ampm = ""
    month = rawDate[4:7]
    match month:
        case "Jan":
            date += "01"
        case "Feb":
            date += "02"
        case "Mar":
            date += "03"
        case "Apr":
            date += "04"
        case "May":
            date += "05"
        case "Jun":
            date += "06"
        case "Jul":
            date += "07"
        case "Aug":
            date += "08"
        case "Sep":
            date += "09"
        case "Oct":
            date += "10"
        case "Nov":
            date += "11"
        case "Dec":
            date += "12"
    date += "-" + rawDate[8:10] + "_"
    if rawDate[12] == ":":
        date += rawDate[11] + "-"
        date += rawDate[13:15]
        ampm = "AM"
    elif rawDate[13] == ":":
        if rawDate[11:13] == "24":
            date += "12"
            ampm = "AM"
        elif int(rawDate[11:13]) > 12:
            date += str(int(rawDate[11:13]) - 12)
            ampm = "PM"
        elif rawDate[11:13] == "12":
            date += "12"
            ampm = "PM"
        date += "\u2236" + rawDate[14:16]
    date += ampm
    return date

class Date:
    def __init__(self, weekday, month, day, hour, minute, ampm, year):
        match weekday:
            case "Sun":
                self.weekday = "Sunday"
            case "Mon":
                self.weekday = "Monday"
            case "Tues":
                self.weekday = "Tuesday"
            case "Wed":
                self.weekday = "Wednesday"
            case "Thu":
                self.weekday = "Thursday"
            case "Fri":
                self.weekday = "Friday"
            case "Sat":
                self.weekday = "Saturday"

        match month:
            case "Jan":
                self.month = "January"
            case "Feb":
                self.month = "February"
            case "Mar":
                self.month = "March"
            case "Apr":
                self.month = "April"
            case "May":
                self.month = "May"
            case "Jun":
                self.month = "June"
            case "Jul":
                self.month = "July"
            case "Aug":
                self.month = "August"
            case "Sep":
                self.month = "September"
            case "Oct":
                self.month = "October"
            case "Nov":
                self.month = "November"
            case "Dec":
                self.month = "December"

        self.day = day

        if int(hour) > 12 and int(hour) != 24:
            self.hour = int(hour) - 12
            self.ampm = "PM"
        elif int(hour) == 12:
            self.hour = hour
            self.ampm = "PM"
        elif int(hour) == 24:
            self.hour = 12
            self.ampm = "AM"
        else:
            self.hour = hour
            self.ampm = "AM"

        if int(minute) < 10:
            self.minute = "0" + str(minute)
        else:
            self.minute = minute

        self.year = year

    def __str__(self):
        return f"{self.weekday}, {self.month} {self.day}, {self.year} at {self.hour}:{self.minute}{self.ampm}"