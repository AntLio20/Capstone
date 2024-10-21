# function to clean up transcript, timestamp/speaker = 0 to remove
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