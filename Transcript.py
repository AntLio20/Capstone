import os
import time
import docx2txt

# Clean up transcript, timestamp/speaker = 0 to remove
def cleanTranscript (text, timestamp, speaker):
    # split each line of text into list
    splitTranscript = text.splitlines(keepends=True)

    # check modes and perform corresponding list item deletions
    if (timestamp == 0) and (speaker == 0):
        del splitTranscript[0::3]
        del splitTranscript[0::2]
    elif (timestamp == 0) and (speaker == 1):
        del splitTranscript[0::3]
    elif (timestamp == 1) and (speaker == 0):
        del splitTranscript[1::3]

    # return text to string format and return it
    text = ""
    for line in splitTranscript:
        text += line
    return text

# Obtain the duration of a meeting
def meetingDuration (transcript):
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
def calculateStart (filepath, rawHours, rawMinutes):
    duration = meetingDuration(filepath)
    minutes = rawMinutes - duration[1]
    if minutes < 0:
        minutes += 60
        hours = rawHours - duration[0] - 1
    else:
        hours = rawHours - duration[0]
    return hours, minutes

# Obtain creation date of transcript file and meeting start time
def extractDate (filepath):
    rawDate = time.ctime(os.path.getctime(filepath))
    transcript = docx2txt.process(filepath)
    if rawDate[9].isspace():
        startTime = calculateStart(transcript, int(rawDate[10:12]), int(rawDate[13:15]))
        date = Date(rawDate[:3], rawDate[4:7], rawDate[8], startTime[0], startTime[1], "", rawDate[19:23])
    else:
        startTime = calculateStart(transcript, int(rawDate[11:13]), int(rawDate[14:16]))
        date = Date(rawDate[:3], rawDate[4:7], rawDate[8:10], startTime[0], startTime[1], "", rawDate[20:24])
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