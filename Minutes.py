# File Name: Minutes.py
# Authors: Javier Chung, Andy Dai, Antonio Lio, Jason Stuckless
# Description: Function for creating a minutes document

import GPT
from docx import Document

def generateMinutes(transcript, minutesFilename):
    # Retrieve summarized meeting notes and section headings from GPT.py
    meetingNotesList, sectionHeadings = GPT.gptSummarization(transcript)

    # Create a new document to store the meeting notes
    summarizedMeetingNotes = Document()

    # Print message informing the user about the creation of docx minutes file
    print("The following has been printed to " + minutesFilename + ":\n")

    # Loop through each section of the meeting notes to put in the document
    for i in range(0, len(meetingNotesList)):
        meetingNotesList[i] = meetingNotesList[i].strip() # formatting it the string so there's no space at the beginning or end
        summarizedMeetingNotes.add_heading(sectionHeadings[i], level = 1)
        summarizedMeetingNotes.add_paragraph(meetingNotesList[i])
        print( sectionHeadings[i] + ": " + meetingNotesList[i] + "\n") # printing it out

    # Save the script to a docx file
    summarizedMeetingNotes.save(minutesFilename)