# File Name: pam.py
# Authors: Javier Chung, Andy Dai, Antonio Lio, Jason Stuckless
# Description: Main file for PAM program

import ActionableItems
import Minutes
import redaction
import Transcript
import GPT as gpt

import docx2txt # remove later

# this function will run the summarization of our program
def summarize(filepath):

    transcript = docx2txt.process(filepath) # remove later

    redactedTranscript = redaction.redact(transcript)

    # Create file name and generate minutes document and summary terminal output
    minutesFilename = Transcript.extractFilenameDate(filepath) + "_minutes.docx" 
    Minutes.generateMinutes(redactedTranscript, filepath, minutesFilename)

    # Identify actionable items
    actionableFilename = Transcript.extractFilenameDate(filepath) + "_actions.txt"
    ActionableItems.outputActionableItems(redactedTranscript, actionableFilename)
