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
import Transcriber
from datetime import datetime
import logging
from pydub import AudioSegment
from speakerID import identify_and_replace_speakers

# Defining global static variables
DIARIZATION_MODEL_CACHE_DIR = "./DiarizationModel"

def transcribeAndDiarize(modelType, file):
    from speakerID import identify_and_replace_speakers  # Safe to re-import inside function if needed

    # File save path
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filepath = os.path.join("./diarizedTranscripts", f"{timestamp}-transcript.docx")

    totalStartTime = time.time()

    # Diarize
    print("loading audio file into diarization model...:\n")
    loadingStartTime = time.time()
    diarization = pipeline({"audio": file})
    loadingEndTime = time.time()
    print(f"speaker-diarization-3.1 loaded in {(loadingEndTime - loadingStartTime):.2f} seconds.\n")

    # Audio segment
    audio = AudioSegment.from_file(file)

    # Build full transcript string
    full_transcript = ""
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        startTime = turn.start
        endTime = turn.end
        text = Transcriber.transcribeAudio(audio, startTime, endTime, modelType)

        full_transcript += f"{startTime} --> {endTime}\n"
        full_transcript += f"{speaker}\n"
        full_transcript += f"{text}\n"

    # Run speaker identification
    full_transcript = identify_and_replace_speakers(full_transcript)

    # Save the transcript to a DOCX file
    doc = Document()
    for line in full_transcript.splitlines():
        doc.add_paragraph(line)
    doc.save(filepath)

    totalEndTime = time.time()
    print(f"Transcript saved in {(totalEndTime - totalStartTime):.2f} seconds at {filepath}")

    return filepath


# muting all the logs 
logging.getLogger("speechbrain").setLevel(logging.ERROR)

# Authenticating with Hugging Face
login(token = "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")

# Setting up the device to perform diarizazation
diarizationProcessor = "mps" if torch.backends.mps.is_available() else "cuda" if  torch.cuda.is_available() else "cpu"

# Loading in both models for speaker diarization
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", cache_dir = DIARIZATION_MODEL_CACHE_DIR)
pipeline.to(torch.device(diarizationProcessor))