import logging
import json
import sounddevice as sd
from queue import Queue, Empty
from vosk import Model, KaldiRecognizer
from rel_path import resource_path
from enums import Phrases

from PySide6.QtCore import QObject, Signal

VOSK_MODEL_PATH = resource_path('./model')          

class VoskVoiceRecognizer(QObject):
    command_successful = Signal(str)
    
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
            raise
            
        self.audio_stream = None
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.obs_controller = obs_controller
        
        self.commands = {
            Phrases.START_REC_PHRASE: (
                'Starting recording',
                [lambda: self.obs_controller.start_recording()]
            ),
            Phrases.STOP_REC_PHRASE: (
                'Stopping recording', 
                [lambda: self.obs_controller.stop_recording()]
            ),
            Phrases.START_REPLAY_PHRASE: (
                'Starting replay', 
                [lambda: self.obs_controller.start_replay_buffer()]
            ),
            Phrases.STOP_REPLAY_PHRASE: (
                'Stopping replay', 
                [lambda: self.obs_controller.stop_replay_buffer()]
            ),
            Phrases.START_EVERYTHING_PHRASE: (
                'Starting all', 
                [lambda: self.obs_controller.start_recording(),
                lambda: self.obs_controller.start_replay_buffer()]
            ),
            Phrases.STOP_EVERYTHING_PHRASE: (
                'Stopping all', 
                [lambda: self.obs_controller.stop_recording(),
                lambda: self.obs_controller.stop_replay_buffer()]
            ),
        }
        
    async def process_audio(self):
        while self.isRunning:
            try:
                data = self.queue.get(timeout=0.1)
                if data is None:
                    break
                
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get('text', '').lower()
                    await self.phrase_handler(text)
            except Empty:
                continue                                               
            except Exception as e:
                self.logger.error(f'Could not process audio: {e}')
                break 
        self.logger.info('Ceased audio processing')
           
    async def phrase_handler(self, text):
        # if text: 
        #     self.logger.info(f'Recognized: {text}')
        
        if any(phrase in text for phrase in Phrases.CLIP_PHRASE.value):
            self.logger.info('CLIP_PHRASE found')
            try:
                await self.obs_controller.save_replay_buffer()
                self.command_successful.emit('Clipping')
            except Exception as e:
                raise
        else:
            # If not a multi phrase command, run through here
            for phrase_key, (response, phrase_commands) in self.commands.items():
                if phrase_key.value in text:
                    signal_emitted = False
                    self.logger.info(f'{phrase_key.name} found')
                    for func in phrase_commands:
                        try:
                            await func()
                            if not signal_emitted:
                                self.command_successful.emit(response)
                                signal_emitted = True
                        except Exception as e:
                            raise
                    
    def voice_callback(self, indata, frames, time, status):
        if status:
            self.logger.warning(f'Audio status: {status}')
        self.queue.put(bytes(indata))
        
    async def start(self):
        self.logger.info('Starting voice recognition')
        self.isRunning = True
        default_input = sd.default.device[0]
        
        try:
            await self.obs_controller.connect()
            
            self.audio_stream = sd.RawInputStream(
                samplerate=16000,
                blocksize=8000,
                device=default_input,
                dtype='int16',
                channels=1,
                callback=self.voice_callback
            )
            self.audio_stream.start()
            await self.process_audio()
        except Exception as e: 
            self.logger.error(f'Could not start audio steam: {e}')
            self.isRunning = False
            raise
    
    async def stop(self):
        self.logger.info('Closing voice recognition')

        self.logger.info('Putting sentinel into the queue')
        self.queue.put(None)
        
        if self.audio_stream.active:
            self.logger.info('Closing audio stream')
            self.audio_stream.close()
            self.audio_stream = None
        try:
            await self.obs_controller.disconnect()
        except Exception as e:
            raise

