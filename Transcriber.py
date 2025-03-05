# File Name: Transcriber.py
# Authors: Javier Chung, Andy Dai, Antonio Lio, Jason Stuckless
# Date: Feb 12, 2025
# Description: This python file transcribes audio segments

# pip install vosk

from vosk import Model, KaldiRecognizer
import json

TRANSCRIPTION_MODEL_PATH = "./TranscriptionModel/vosk-model-en-us-0.22"

# Loading the transcription model
voskModel = Model(TRANSCRIPTION_MODEL_PATH)

def transcribeAudio(audio, frameRate, startTime, endTime):

    # Creating the KaldiRecognizer with the transcription model
    rec = KaldiRecognizer(voskModel, frameRate)

    # segementing the speakers audio clip
    audio.setpos(int(startTime * frameRate))  
    segmentedFrames = int((endTime - startTime) * frameRate)
    audioSegment = audio.readframes(segmentedFrames)

    # Transcribing the audio segment
    rec.AcceptWaveform(audioSegment)
    result = json.loads(rec.FinalResult())
    text = result["text"]

    return text
