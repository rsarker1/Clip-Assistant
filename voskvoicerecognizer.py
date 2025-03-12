import logging
import sys
from queue import Queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer

VOSK_MODEL_PATH = './model'
SAMPLE_RATE = 16000

class VoskVoiceRecognizer:
    def __init__(self, obs_controller):
        self.queue = Queue()
        self.logger = logging.getLogger(__name__)
        self.isRunning = False
        
        try:
            self.model = Model(VOSK_MODEL_PATH)
            self.logger.info(f"Loaded Vosk model from {VOSK_MODEL_PATH}")
        except Exception as e:
            self.logger.error(f"ERROR: Failed to load Vosk model, {e}")
            sys.exit(1)
            
        self.recognizer = KaldiRecognizer(self.model, SAMPLE_RATE)
        self.obs_controller = obs_controller
    def process_audio(self):
        while self.isRunning:
            try:
                data = self.queue.get()
                if self.recognizer.AcceptWaveform(data):
                    voice = self.recognizer.Result()
            except Exception as e:
                