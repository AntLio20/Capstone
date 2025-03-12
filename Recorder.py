# File Name: Recorder.py
# Authors: Javier Chung, Andy Dai, Antonio Lio, Jason Stuckless
# Date: Jan 22, 2025
# Description: This python file is used to record live audio

# libraries needed 
# brew install portaudio
# pip install pyaudio

import wave
import pyaudio
import threading

def recordAudio():
    filename = "tmpRecording.wav"
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    voiceDetectionAudio = pyaudio.PyAudio()


    stream = voiceDetectionAudio.open(format=FORMAT,
                                      channels=CHANNELS,
                                      rate=RATE, 
                                      input=True, 
                                      frames_per_buffer=CHUNK)

    print("Currently Recording...")

    setStopRecording(False)


    frames = []

    isRecording.set() # starting the recording proccess by setting the state to true which signals thread to continue running

    # creating a thread to track when a user wants to interrupt and terminate the recording
    intruptThread = threading.Thread(target=isDoneRecording)
    intruptThread.start()

    # Recording live audio
    while isRecording.is_set():
        data = stream.read(CHUNK)
        frames.append(data)

    # Ensure the intruptThread has finished before proceeding
    intruptThread.join()

    print("DONE RECORDING...")

    stream.stop_stream()
    stream.close()
    voiceDetectionAudio.terminate()

    # Saving the recorded audio as a wave file
    waveFile = wave.open(filename, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(voiceDetectionAudio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

# this function uses another thread to poll a keyboard input that will end the recording of a user
def isDoneRecording():
    while isRecording.is_set():

        if(getStopRecording() == True):
            isRecording.clear() # finishing execution of the thread and clearing state

            
def getStopRecording():
    return stopRecording

def setStopRecording(isStop):
    global stopRecording
    stopRecording = isStop

stopRecording = False

# Declaring a variable that creates an event object that a thread can track
isRecording = threading.Event() # set to cleared state

