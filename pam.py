# File Name: pam.py
# Authors: Javier Chung, Andy Dai, Antonio Lio, Jason Stuckless
# Description: Main file for PAM program

import Minutes
import Transcript

import docx2txt # remove later

# this function will run the summarization of our program
def summarize(filepath, model):

    transcript_type = Transcript.detectTranscriptFormat(filepath)

    if transcript_type == 1:
        transcript = docx2txt.process(filepath)
    elif transcript_type == 2:
        transcript = Transcript.convertMeet(filepath)
    elif transcript_type == 3:
        transcript = Transcript.convertZoom(filepath)
    elif transcript_type == 4:
        transcript = Transcript.convertDiarization(filepath)
    elif transcript_type == 0:
        print("Invalid Transcript Format")
        transcript = "" # Need to allow for this in GUI with error message and end before summarization

    redactedTranscript = redaction.redact(transcript)

    # Create file name and generate minutes document and summary terminal output
    minutesFilename = Transcript.extractFilenameDate(filepath) + "_minutes.docx" 
    Minutes.generateMinutes(redactedTranscript, filepath, minutesFilename)

    # Identify actionable items
    actionableFilename = Transcript.extractFilenameDate(filepath) + "_actions.txt"
    ActionableItems.outputActionableItems(redactedTranscript, actionableFilename)
