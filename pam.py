# File Name: pam.py
# Authors: Javier Chung, Andy Dai, Antonio Lio, Jason Stuckless
# Description: Main file for PAM program

import ActionableItems
import Minutes
import Redaction
import Transcript

# HOW IS pam.py CALLING THE GUI AND RETRIEVING THE FILEPATH?????
# This does not run right now

# Perform transcript redaction
# redaction currently incomplete, remove comment from line below when complete
# redactedTranscript = Redaction.redact(filepath)

# FOR TESTING ONLY
filepath = "transcript02.docx"
import docx2txt
redactedTranscript = docx2txt.process(filepath)
# REMOVE LATER

# Create file name and generate minutes document and summary terminal output
minutesFilename = Transcript.extractFilenameDate(filepath) + "_minutes.docx"
Minutes.generateMinutes(redactedTranscript, minutesFilename)

# Identify actionable items
actionableFilename = Transcript.extractFilenameDate(filepath) + "_actions.txt"
ActionableItems.outputActionableItems(redactedTranscript, actionableFilename)