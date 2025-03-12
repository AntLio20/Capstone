# File Name: Transcriber.py
# Authors: Javier Chung, Andy Dai, Antonio Lio, Jason Stuckless
# Date: Feb 12, 2025
# Description: This python file transcribes audio segments

# pip install openai-whisper
# pip install pydub
# pip install audioSegment

import whisper
from pydub import AudioSegment
import os
import numpy as np

# Loading the transcription model
TRANSCRIPTION_MODEL_DIR = './TranscriptionModel'
modelMeduim = whisper.load_model("medium.en", download_root=TRANSCRIPTION_MODEL_DIR) # there is tiny, base, medium, large
modelBase = whisper.load_model("base.en", download_root=TRANSCRIPTION_MODEL_DIR) # there is tiny, base, medium, large
modelTiny = whisper.load_model("tiny.en", download_root=TRANSCRIPTION_MODEL_DIR) # there is tiny, base, medium, large
def transcribeAudio(audio, startTime, endTime, modelType):

    # Converting the times to miliseconds
    startTime = startTime * 1000
    endTime = endTime * 1000

    # Segmenting the frame that the speaker is speaking
    audioSegment = audio[startTime:endTime]

    # Converting the audio clip into a numpy array for the model to use
    audioArray = np.array(audioSegment.get_array_of_samples())
    # normalizing the array to 16 bit integers (2 ^ 16) as that is what the whisper model expects
    audioArray = audioArray.astype(np.float32) / (2**15) 

    # Performing transcription on the audio segment
    if (modelType == 0):
        result = modelMeduim.transcribe(audioArray)
    elif( modelType == 1):
        result = modelBase.transcribe(audioArray)
    elif( modelType == 2):
        result = modelTiny.transcribe(audioArray)
    
    return result["text"]
