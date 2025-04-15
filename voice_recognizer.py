import logging
import sys
import json
import asyncio
from enum import Enum
import threading
from queue import Queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer

from PySide6.QtCore import QObject, Signal, Slot

VOSK_MODEL_PATH = './model'           
SAMPLE_RATE = 16000                   # Frequency for human voice

class Phrases(Enum):
    START_REC_PHRASE = 'freya start recording'
    STOP_REC_PHRASE = 'freya stop recording'
    START_REPLAY_PHRASE = 'freya start the replay'
    STOP_REPLAY_PHRASE = 'freya stop the replay'
    START_EVERYTHING_PHRASE = 'freya start everything'
    STOP_EVERYTHING_PHRASE = 'freya stop everything'
    CLIP_PHRASE = ['freya clip it', 'freya clip that']

class VoskVoiceRecognizer(QObject):
    def __init__(self, obs_controller):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        self.queue = Queue()
        self.isRunning = False
        
        try:
            self.model = Model(VOSK_MODEL_PATH)
            self.logger.info(f'Loaded Vosk model from {VOSK_MODEL_PATH}')
        except Exception as e:
            self.logger.error(f'Failed to load Vosk model: {e}')
            sys.exit(1)
            
        self.recognizer = KaldiRecognizer(self.model, SAMPLE_RATE)
        self.obs_controller = obs_controller
        
        self.commands = {
            Phrases.START_REC_PHRASE.value: (
                "START_REC_PHRASE found",
                [lambda: self.obs_controller.start_recording()]
            ),
            Phrases.STOP_REC_PHRASE.value: (
                "STOP_REC_PHRASE found", 
                [lambda: self.obs_controller.stop_recording()]
            ),
            Phrases.START_REPLAY_PHRASE.value: (
                "START_REPLAY_PHRASE found", 
                [lambda: self.obs_controller.start_replay_buffer()]
            ),
            Phrases.STOP_REPLAY_PHRASE.value: (
                "STOP_REPLAY_PHRASE found", 
                [lambda: self.obs_controller.stop_replay_buffer()]
            ),
            Phrases.START_EVERYTHING_PHRASE.value: (
                "START_EVERYTHING_PHRASE found", 
                [lambda: self.obs_controller.start_recording(),
                lambda: self.obs_controller.start_replay_buffer()]
            ),
            Phrases.STOP_EVERYTHING_PHRASE.value: (
                "STOP_EVERYTHING_PHRASE found", 
                [lambda: self.obs_controller.stop_recording(),
                lambda: self.obs_controller.stop_replay_buffer()]
            ),
        }
        
    async def process_audio(self):
        while self.isRunning:
            try:
                data = self.queue.get()
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get('text', '').lower()
                    
                    await self.phrase_handler(text)
                                                          
            except Exception as e:
                self.logger.error(f'Could not process audio: {e}')
                sys.exit(1)      
    
    async def phrase_handler(self, text):
        if text: 
            self.logger.info(f'Recognized: {text}')
        
        if any(phrase in text for phrase in Phrases.CLIP_PHRASE.value):
            self.logger.info('CLIP_PHRASE found')
            await self.obs_controller.save_replay_buffer()
        
        # If not a multi phrase command, run through here
        for phrase_key, (log_info, phrase_commands) in self.commands.items():
            if phrase_key in text:
                self.logger.info(log_info)
                for func in phrase_commands:
                    await func()
                    
    def voice_callback(self, indata, frames, time, status):
        if status:
            self.logger.warning(f'Audio status: {status}')
        self.queue.put(bytes(indata))
        
    async def start(self):
        self.isRunning = True
        default_input = sd.default.device[0]
        
        await self.obs_controller.connect()
        try:
            with sd.RawInputStream(
                samplerate=SAMPLE_RATE,
                blocksize=8000,
                device=default_input,
                dtype='int16',
                channels=1,
                callback=self.voice_callback
            ):
                await self.process_audio()

        except Exception as e:
            self.logger.error(f'Could not start audio steam: {e}')
            self.isRunning = False
            
    async def stop(self):
        self.isRunning = False
        await self.obs_controller.disconnect()

