import logging
import sys
import json
import threading
from queue import Queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer

VOSK_MODEL_PATH = './model'           
SAMPLE_RATE = 16000                   # Frequency for human voice

class VoskVoiceRecognizer:
    def __init__(self, obs_controller):
        self.queue = Queue()
        self.logger = logging.getLogger(__name__)
        self.isRunning = False
        
        try:
            self.model = Model(VOSK_MODEL_PATH)
            self.logger.info(f'Loaded Vosk model from {VOSK_MODEL_PATH}')
        except Exception as e:
            self.logger.error(f'Failed to load Vosk model: {e}')
            sys.exit(1)
            
        self.recognizer = KaldiRecognizer(self.model, SAMPLE_RATE)
        self.obs_controller = obs_controller
        
    def process_audio(self):
        while self.isRunning:
            try:
                data = self.queue.get()
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get('text', '').lower()
                    
                    if text:
                        self.logger.debug(f'Recognized: {text}')
                        
                        if 'test' in text:
                            self.logger.info('IT WORKS')
                    
            except Exception as e:
                self.logger.error(f'Could not process audio: {e}')
                sys.exit(1)
                
                
    def query_input_device(self):
        device_info = sd.query_devices()
    
    
    def start(self):
        self.running = True
        
        # try:
        #     with sd.RawInputStream(
        #         samplerate=SAMPLE_RATE,
        #         blocksize=8000,
        #         device=
        #     ):
                
