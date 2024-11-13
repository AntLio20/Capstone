import os
import docx2txt
import openai
import tiktoken
import Transcript
from datetime import datetime

# Define global variables
currentTime = datetime.now()
dt_string = currentTime.strftime("%B %d, %Y %H:%M:%S")
meetingNotesList = []
sectionHeadings = ["Opening", "Present", "Absent", "Agenda Approval", "Previous Meeting Approval",
                   "Previous Meeting Summary", "Summary of Meeting", "Adjournment"]


# function converts the transcript into chunks where it would be stored into an array
def chunkToText(transcript, max_token, totalChunks = 0):
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
        totalChunks += 1
    return chunks, totalChunks


def gptSummarization(transcript, filepath):
    openai.api_key = os.getenv(
        "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")
    # Connecting to OpenAI
    # key = "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"

    # initializing a list that will store different parts of the summarized transcript
    global meetingNotesList
    meetingNotesList = []
    sectionHeadings = ["Opening", "Present", "Absent", "Agenda Approval", "Previous Meeting Approval",
                       "Previous Meeting Summary", "Summary of Meeting", "Adjournment"]

    # initializing a counter for each section
    sectionCounter = 0

    # converts the document to a string
    #transcript = docx2txt.process(filepath)
    max_tokens = 15000

    # extracts the date and time of transcript creation for use in minutes and file naming
    date = Transcript.extractFormalDate(filepath)

    # calls function to separate string into chunks each fitting the max tokens
    transcript_chunks, totalChunks = chunkToText(transcript, max_tokens)

    # designates the chunk number to gpt
    chunkCounter = 1
    print(f"Summarization Date: " + dt_string + "\n")
    print(f"Your transcript will be split into a total of {totalChunks} chunks\n")

    # this code below is used to submit a prompt to the OpenAI API, a for loop to go through all chunks
    print("Currently processing each chunk: \n")
    for chunk in transcript_chunks:
        print(f"Chunk number #{chunkCounter}\n")
        completion = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "assistant", "content": "You are a helpful secretary."},
                {
                    "role": "user",
                    "content": (
                        f"Organize the transcript into different sections "
                        "using '☺' in between each section."
                        "Please format as follows:\n"
                        "1. Opening information, this will include date of meeting, start time , end Time (start time + (last timestamp - first timestamp), dont need to mention this part) \n"
                        "2. Present members, if the person is designated as host, put a '(Host)' tag beside their name\n"
                        "3. Absent members\n"
                        "4. Agenda approval\n"
                        "5. Previous meeting minutes approval\n"
                        "6. Summary of last meeting notes and decisions\n"
                        "7. Detailed summary and key points of the topic of the current meeting\n"
                        "8. Adjournment time, bascially the end time\n"
                        "only reply with the answer to each section with the '☺' in between each section\n"
                        f"(Processing chunk #{chunkCounter}): {chunk}"
                    )
                }
            ],
            # this is used to get real time response word for word
            stream=True,
            temperature=0,
        )

        # Process streaming responses
        response_text = ""
        for part in completion:
            # Access 'content' directly and check if it's not None
            content = part.choices[0].delta.content
            if content is not None:
                response_text += content

        # Split sections by the delimiter "☺" and append to meeting notes
        for section in response_text.split("☺"):
            meetingNotesList.append(section.strip())

        # increase chunk counter to move to the next chunk
        chunkCounter += 1

    # Displays the organized meeting notes
    print("----------------------------------------------------")
    print("Meeting Summary: \n")

    # assigns each section of the meeting notes to the header of each section
    for heading, note in zip(sectionHeadings, meetingNotesList):
        print(f"{note}\n")
