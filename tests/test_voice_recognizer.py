import pytest
import asyncio
import json

import voice_recognizer as vr
from voice_recognizer import VoskVoiceRecognizer
from enums import Phrases

@pytest.fixture(autouse=True)
def disable_audio_and_model(monkeypatch):
    class FakeModel:
        def __init__(self, path):
            pass

    class FakeKaldiRecognizer:
        def __init__(self, model, rate):
            pass
        
        def AcceptWaveform(self, data):
            return False
        
        def Result(self):
            return json.dumps({'text': ''})

    class FakeInputStream:
        def __init__(self, *, callback, **kwargs):
            self.callback = callback
            self.active = False
            
        def start(self):
            self.active = True
            
        def stop(self):
            self.active = False
            
        def close(self):
            self.active = False
            
        def __enter__(self): return self
        def __exit__(self, exc_type, exc, tb): pass

    monkeypatch.setattr(vr, 'Model', FakeModel)
    monkeypatch.setattr(vr, 'KaldiRecognizer', FakeKaldiRecognizer)
    monkeypatch.setattr(vr.sd, 'RawInputStream', FakeInputStream)
    yield

class DummyController:
    def __init__(self):
        self.actions = []
        self.connected = False
        self.disconnected = False

    async def connect(self):
        self.connected = True

    async def disconnect(self):
        self.disconnected = True

    async def start_recording(self):
        self.actions.append('start_recording')

    async def stop_recording(self):
        self.actions.append('stop_recording')

    async def start_replay_buffer(self):
        self.actions.append('start_replay')

    async def stop_replay_buffer(self):
        self.actions.append('stop_replay')

    async def save_replay_buffer(self):
        self.actions.append('save_replay')
    
def test_voice_callback_puts_bytes_in_queue():
    controller = DummyController()
    recognizer = VoskVoiceRecognizer(controller)
    sample = b'\x00\x01\x02'
    recognizer.voice_callback(sample, None, None, None)

    assert recognizer.queue.get_nowait() == sample

@pytest.mark.asyncio
async def test_phrase_handler_triggers_commands_and_signal(monkeypatch):
    controller = DummyController()
    recognizer = VoskVoiceRecognizer(controller)
    emitted = []
    recognizer.command_successful.connect(lambda msg: emitted.append(msg))
    
    # Test single command
    await recognizer.phrase_handler(Phrases.START_REC_PHRASE.value)
    assert 'start_recording' in controller.actions
    assert 'Starting recording' in emitted

    controller.actions.clear()
    emitted.clear()

    # Test multi command
    await recognizer.phrase_handler(Phrases.STOP_EVERYTHING_PHRASE.value)
    assert controller.actions == ['stop_recording', 'stop_replay']
    assert emitted == ['Stopping all']

@pytest.mark.asyncio
async def test_phrase_handler_clipping(monkeypatch):
    controller = DummyController()
    recognizer = VoskVoiceRecognizer(controller)

    clipped = []
    recognizer.command_successful.connect(lambda msg: clipped.append(msg))

    # any phrase containing clip
    await recognizer.phrase_handler('freya clip it')
    assert controller.actions == ['save_replay']
    assert clipped == ['Clipping']
    
@pytest.mark.asyncio
async def test_stop_cleans_queue_and_stream(monkeypatch):
    controller = DummyController()
    recognizer = VoskVoiceRecognizer(controller)

    recognizer.audio_stream = vr.sd.RawInputStream(
        samplerate=16000, blocksize=8000, device=0,
        dtype='int16', channels=1, callback=lambda *args: None
    )
    recognizer.audio_stream.start()
    assert recognizer.audio_stream.active

    await recognizer.stop()
    assert recognizer.isRunning is False
    assert recognizer.audio_stream is None
    assert recognizer.queue.get_nowait() is None