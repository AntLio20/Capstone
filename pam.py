# File Name: pam.py
# Authors: Javier Chung, Andy Dai, Antonio Lio, Jason Stuckless
# Description: Main file for PAM program

import ActionableItems
import Minutes
import Transcript

import docx2txt # remove later


# HOW IS pam.py CALLING THE GUI AND RETRIEVING THE FILEPATH?????
# This does not run right now

# Perform transcript redaction
# redaction currently incomplete, remove comment from line below when complete
# redactedTranscript = Redaction.redact(filepath)


# this function will run the summarization of our program
def summarize(filepath):

    redactedTranscript = docx2txt.process(filepath) # remove later

    # call to create a summaraization of the transcript with GPT
    # gpt.gptSummarization(redactedTranscript, filepath)

    # Create file name and generate minutes document and summary terminal output
    minutesFilename = Transcript.extractFilenameDate(filepath) + "_minutes.docx" 
    Minutes.generateMinutes(redactedTranscript, filepath, minutesFilename)

    # Identify actionable items
    actionableFilename = Transcript.extractFilenameDate(filepath) + "_actions.txt"
    ActionableItems.outputActionableItems(redactedTranscript, actionableFilename)