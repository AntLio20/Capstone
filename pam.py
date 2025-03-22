# File Name: pam.py
# Authors: Javier Chung, Andy Dai, Antonio Lio, Jason Stuckless
# Description: Main file for PAM program

import Minutes
import Transcript
import GPT as gpt
import docx2txt
import testing as deepseekLocal

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

    # WORK WITH transcript IN THE SUMMARIZATIONS

    # deepseek r1 model for summarization, redaction and actionable items
    if (model == 0):
        print("r1 model code")
        deepseekLocal.deepseekr18b(transcript)

    # deepseek api model for summarization, redaction and actionable items
    elif (model == 1):
        gpt.deepseekAPI(transcript)
        print("deepseek api model code")

    # openai api model for summarization, redaction and actionable items
    elif (model == 2):
        print("open api model code")
        print(gpt.gptSummarization(transcript))


    # Create file name and generate minutes document and summary terminal output
    minutesFilename = Transcript.extractFilenameDate(filepath) + "_minutes.docx" 
    Minutes.generateMinutes(redactedTranscript, filepath, minutesFilename)

    # Identify actionable items
    actionableFilename = Transcript.extractFilenameDate(filepath) + "_actions.txt"
    ActionableItems.outputActionableItems(redactedTranscript, actionableFilename)
