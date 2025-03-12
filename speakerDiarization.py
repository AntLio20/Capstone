# File Name: speakerDiarization.py
# Authors: Javier Chung, Andy Dai, Antonio Lio, Jason Stuckless
# Date: Jan 25, 2025
# Description: This python file is convert an audio file into a speaker diarized transcript

# install this if you have a mac m1/m2 chip-  pip install torch torchvision torchaudio -f https://download.pytorch.org/whl/metal.html
# install this if you have a gpu - pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# on windows
# sudo apt-get update && sudo apt-get install -y ffmpeg libsndfile1 rm -rf /var/lib/apt/lists/*

# on mac
# brew install ffmpeg libsndfile

# Depenencies
# pip install --upgrade pip
# pip install pyannote.audio torch pytorch-lightning
# pip install huggingface_hub
# pip install python-docx

from pyannote.audio import Pipeline
from huggingface_hub import login
import torch
from pyannote.audio import Model
from pyannote.audio.pipelines import SpeakerDiarization
import time
import math
import os
from docx import Document
import wave
import Transcriber
from datetime import datetime
import logging

# Defining global static variables
AUDIO_FILE = "tmpRecording.wav"
DIARIZATION_MODEL_CACHE_DIR = "./DiarizationModel"
TRANSCRIPT_DIR = "./diarizedTranscripts"

def transcribeAndDiarize():

    # Setting the file path to the desktop of the host OS
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filepath = os.path.join(TRANSCRIPT_DIR, f"{timestamp}-transcript.docx")

    totalStartTime = time.time()

    # applying pretrained pipeline to the audio clip
    print("loading audio file into diarization model...:\n")
    loadingStartTime = time.time()
    diarization = pipeline({"audio": AUDIO_FILE})
    loadingEndTime = time.time()
    elapsedLoadingtimeMin = int((loadingEndTime - loadingStartTime)//60)
    elapsedLoadingTimeSec = int(math.ceil((loadingEndTime - loadingStartTime)%60))
    print(f"speaker-diarization-3.1 has successfully loaded and diarizaed the audio file with the time of {elapsedLoadingtimeMin} mins and {elapsedLoadingTimeSec} secs \n\n\n\n")

    # Creating a new document to store the transcript
    doc = Document()

    # opening audiofile
    audio = wave.open(AUDIO_FILE, "rb")
    frameRate = audio.getframerate()

    # converting the audio clip into a trascription
    for turn, _, speaker in diarization.itertracks(yield_label=True):

        # getting the time started and ended of the segment that one speaker spoke for
        startTime = turn.start
        endTime = turn.end

        text = Transcriber.transcribeAudio(audio, frameRate, startTime, endTime)

        doc.add_paragraph(f"{startTime} --> {endTime}")
        doc.add_paragraph(f"{speaker}")
        doc.add_paragraph(f"{text}\n")

    # saving the document
    doc.save(filepath)

    totalEndTime = time.time()

    elapsedtotaltimeMin = (int)((totalEndTime - totalStartTime)//60)
    elapsedTotalTimeSec = (int)(math.ceil((totalEndTime - totalStartTime)%60))

    print(f"Finished Creating Transcript with time of {elapsedtotaltimeMin} mins and {elapsedTotalTimeSec} secs")

    return(filepath)

# deleting the audio file as it is no longer needed
def deleteAudioFile():
    if os.path.exists(AUDIO_FILE):
        os.remove(AUDIO_FILE)

# muting all the logs 
logging.getLogger("speechbrain").setLevel(logging.ERROR)

# Authenticating with Hugging Face
login(token = "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")

# Setting up the device to perform diarizazation
diarizationProcessor = "mps" if torch.backends.mps.is_available() else "cuda" if  torch.cuda.is_available() else "cpu"

# Loading in both models for speaker diarization
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", cache_dir = DIARIZATION_MODEL_CACHE_DIR)
pipeline.to(torch.device(diarizationProcessor))
