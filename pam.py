# File Name: pam.py
# Authors: Javier Chung, Andy Dai, Antonio Lio, Jason Stuckless
# Date: Sept 12, 2024
# Description: This is the main python file for an automated meeting summarizer application

import os
import docx2txt
import tiktoken
import Transcript
import outputNER
from openai import OpenAI
from docx import Document

# ----------------------------- Functions -----------------------------------------------

# function converts the transcript into chunks where it would be stored into an array
def chunktoText(transcript, max_token):
    # gpt-4o is being used for the tokenization
    encoding = tiktoken.encoding_for_model("gpt-4o")
    tokens = encoding.encode(transcript)

    # sets up an array to hold the list of chunks
    chunks = []

    # goes through the transcript and chops it up into chunks
    i = 0
    while i < len(tokens):
        chunk = tokens[i:i + max_token]
        chunks.append(encoding.decode(chunk))
        i = i + max_token
    return chunks

# this function returns the summarized meeting notes
def getMeetingNotes():
    return meetingNotesList;

# this function returns the headings
def getSectionHeadings():
    return sectionHeadings;



# ----------------------------------------- Main Method ------------------------------------------------

# Connecting to OpenAI
key = "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"

client = OpenAI(
    api_key=os.environ.get(key),
)

# initializing a list that will store different parts of the summarized transcript
meetingNotesList = []
sectionHeadings = ["Opening", "Present", "Absent", "Agenda Approval", "Previous Meeting Approval" ,"Previous Meeting Summary", "Summary of Meeting", "Adjournment"]

# initializing a counter for each section
sectionCounter = 0

# converts the document to a string
filepath = "trans.docx"
transcript = docx2txt.process(filepath)
max_tokens = 6000

# extracts the date and time of transcript creation for use in minutes and file naming
date = Transcript.extractFormalDate(filepath)

# calls function to separate string into chunks each fitting the max tokens
transcript_chunks = chunktoText(transcript, max_tokens)

# designates the chunk number to gpt
chunkCounter = 1

# this code below is used to submit a prompt to the OpenAI API, a for loop to go through all chunks
for chunk in transcript_chunks:

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "assistant", "content": "You are a helpful secretary."},
            {
                "role": "user",
                "content": (
                    f"Organize the transcript created on into different sections using '☺' in between each section (not at the beginning or end) and dont include any headings and /n's , 1. (opening) Who hosted the meeting on {date} , 2. Present (all present members), 3. Absent (all absent members), 4. The agenda and if it was approved, 5. The minutes from the previous meeting were reviewed and approved, 6. Summary of the last meeting notes and decisions made, 7. A detailed summary of the current meeting including new topics and decisions/motions, 8. The ajournment of the meeting and the time of it (chunk #{chunkCounter}): {chunk}"
                )
            }
        ],
        # this is used to get real time response word for word
        stream=True,
        temperature=0,
    )
    chunkCounter += 1

# partitioning the summarized transcript into different parts in a meeting minute document using the live response
for chunk in completion: # this takes each piece of the live response object within the created completion

    # getting the response of openAI where choice includes the delta, index and finish_reason
    response = chunk.choices

    # checking if the first response exists and delta which contains the role and content exist and if delta has any content within it
    if response and response[0].delta and response[0].delta.content:

        # splitting the response into single words
        words = response[0].delta.content.split()

        # dividing the sections up using the delimiter ☺
        for word in words:
            if (word == '☺'):
                sectionCounter += 1
                meetingNotesList.append("")
            else:
                # ensuring that the list is not out of range
                if (len(meetingNotesList) <= sectionCounter):
                    meetingNotesList.append("")
                meetingNotesList[sectionCounter] = (meetingNotesList[sectionCounter] + response[0].delta.content)

        # printing out the content live
        # print(response[0].delta.content, end = '', flush = True) 
            

# creating a new document to store the meeting notes
summarizedMeetingNotes = Document()

# set name of file
minutesFilename = Transcript.extractFilenameDate(filepath) + "_minutes.docx"

# print message informing the user about the creation of docx minutes file
print("The following has been printed to " + minutesFilename + ":\n")

# loops through each section of the meeting notes to put in the document
for i in range(0, len(meetingNotesList)):
    meetingNotesList[i] = meetingNotesList[i].strip() # formatting it the string so there's no space at the beginning or end
    summarizedMeetingNotes.add_heading(sectionHeadings[i], level = 1)
    summarizedMeetingNotes.add_paragraph(meetingNotesList[i])
    print( sectionHeadings[i] + ": " + meetingNotesList[i] + "\n") # printing it out

# saves the script to a docx file
summarizedMeetingNotes.save(minutesFilename)

# create visualizations for NER using SpaCy platform 
outputNER.createNerOutput(filepath)

# open transcript NER and transcript dependencies html documents
os.system("start transcript.html")
os.system("start transcriptDependencies.html")
