import asyncio
import pytest
from PySide6.QtWidgets import QWidget
from voice_thread import VoiceRecognizerThread

class DummyRecognizer:
    def __init__(self):
        self.isRunning = True
        self.stop_called = False

    async def start(self):
        pass

    async def stop(self):
        self.stop_called = True
        
class DummyLoop:
    def __init__(self, loop_running=True):
        self.loop_running = loop_running
        self.stopped = False
        self.created_tasks = []
        self.soon_calls = []

    def is_running(self):
        return self.loop_running

    def run_forever(self):
        pass

    def stop(self):
        self.stopped = True
        self.loop_running = False

    def call_soon_threadsafe(self, func):
        self.soon_calls.append(func)

    def create_task(self, coro):
        task = asyncio.ensure_future(coro)
        self.created_tasks.append(task)
        return task

    def close(self):
        pass
    
@pytest.fixture
def thread(qtbot):
    recognizer = DummyRecognizer()
    voice_thread = VoiceRecognizerThread(recognizer)
    qtbot.addWidget(QWidget()) 
    return voice_thread

def make_future(result=None, exc: Exception = None):
    fut = asyncio.Future()
    if exc is not None:
        fut.set_exception(exc)
    else:
        fut.set_result(result)
    return fut

def test_req_stop_sets_flag(thread):
    assert thread.voice_recognizer.isRunning
    thread.req_stop()
    assert thread.voice_recognizer.isRunning is False
    
def test_on_completion_success(thread):
    fut = make_future(result=None)
    loop = DummyLoop(loop_running=True)
    thread.exec_loop = loop
    thread.on_completion(fut)

    assert thread.voice_recognizer.isRunning is False
    assert any(isinstance(t, asyncio.Future) for t in loop.created_tasks)
    assert loop.stopped or any(call == loop.stop for call in loop.soon_calls)
    
def test_on_completion_failure_emits_error_and_stops(qtbot, thread):
    exc = RuntimeError('Connection failed')
    fut = make_future(exc=exc)
    loop = DummyLoop(loop_running=True)
    thread.exec_loop = loop

    captured = []
    thread.error_occured.connect(lambda msg: captured.append(msg))
    thread.on_completion(fut)
    
    assert len(captured) == 1
    assert 'Could not connect to OBS' in captured[0]

    assert loop.stopped
    
def test_run_creates_and_closes_loop(monkeypatch, thread):
    monkeypatch.setattr(asyncio, 'new_event_loop', lambda: DummyLoop(loop_running=False))
    monkeypatch.setattr(asyncio, 'set_event_loop', lambda loop: None)

    async def dummy_start():
        return
    thread.voice_recognizer.start = dummy_start
    thread.run()

    assert isinstance(thread.exec_loop, DummyLoop)
    assert thread.exec_loop.loop_running is False