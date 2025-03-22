# Capstone Group 4
**Pam** - Automated minutes taker / meeting summarizer 

Faculty Advisor: Dr. Masoud Makrehchi  
Capstone Coordinator: Dr. Q. Mahmoud

# Introduction
The repository contains a program that will automatically summarize meeting any given meeting transcripts. 

## Features
- Record audio
- Transcribe and perform speaker siarization on audio clips
- Summarize transcriptions
- Redact off topic conversations
- produce actionable items
 
## Requirements
- Python version: **python3.12**
  
Libraries:
- ffmpeg
- libsndfile
- pyannote.audio
- torch
- pytorch-lightning
- huggingface_hub
- python-docx
- openai-whisper
- audioSegment
- pyaudio
- PyQt5
- python-docx
- Pillow
- openai
- tiktoken
- docx2txt

# Usage

**Mac silicon chip OS Specific Depenencies**

```bash
pip install torch torchvision torchaudio -f https://download.pytorch.org/whl/metal.html
brew install ffmpeg libsndfile
brew install portaudio
```

**Window OS Specific Depenencies**

Only if you have a GPU:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

Speaker ID:
```bash
python -m spacy download en_core_web_lg
```

**For all OS**
```bash
pip install pyannote.audio torch pytorch-lightning
pip install huggingface_hub
pip install python-docx
pip install openai-whisper
pip install audioSegment
pip install pyaudio
pip install PyQt5
pip install python-docx
pip install Pillow
pip install openai
pip install tiktoken
pip install docx2txt
pip install numpy
pip install scikit-learn
```

Clone and go to the repository 
```bash
git clone https://github.com/AntLio20/Capstone
```
Execute Script
```bash
python gui.py
```
