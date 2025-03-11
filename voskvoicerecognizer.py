import logging
import vosk
import queue

VOSK_MODEL_PATH = './model'

def class VoskVoiceRecognizer:
    def __init__(self):
        