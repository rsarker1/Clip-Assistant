import pytest
from freya_app import Freya_for_OBS
from enums import Options
from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QIcon

class DummyApp:
    def setWindowIcon(self, icon): pass
    def setQuitOnLastWindowClosed(self, flag): pass
    def exec(self): self.ran = True
    def quit(self): self.quit_called = True
    
class DummyTrayIcon:
    Information = 1
    
    def __init__(self, *args, **kwargs): self.visible = False
    def setContextMenu(self, menu): pass
    def show(self): self.visible = True
    def setToolTip(self, text): self.tooltip = text
    def showMessage(self, title, msg, icon, duration): self.msg = (title, msg, icon, duration)

class DummyRecognizer:
    def __init__(self): self.command_successful = DummySignal()

class DummyThread:
    def __init__(self): self.error_occured = DummySignal()
    def start(self): self.started = True
    def isRunning(self): return True
    def req_stop(self): self.stopped = True
    def wait(self): self.waited = True
    def quit(self): self.quitted = True

class DummySignal:
    def connect(self, slot): self.slot = slot

class DummyTTS:
    def say(self, msg): self.msg = msg
    def runAndWait(self): self.ran = True

@pytest.fixture(autouse=True)
def patch_freya(qtbot, monkeypatch):
    monkeypatch.setattr('freya_app.QApplication', lambda: DummyApp())
    monkeypatch.setattr('freya_app.QSystemTrayIcon', DummyTrayIcon)
    monkeypatch.setattr('freya_app.load_config', lambda: {'host': 'localhost', 'port': 4455, 'password': 'pass'})
    monkeypatch.setattr('freya_app.OBSRecordingController', lambda host, port, password: None)
    monkeypatch.setattr('freya_app.VoskVoiceRecognizer', lambda obs: DummyRecognizer())
    monkeypatch.setattr('freya_app.VoiceRecognizerThread', lambda rec: DummyThread())
    monkeypatch.setattr('freya_app.pyttsx3.init', lambda: DummyTTS())

@pytest.mark.usefixtures('patch_freya')
def test_app_initialization():
    app = Freya_for_OBS()
    assert isinstance(app.app, DummyApp)
    assert isinstance(app.tray_icon, DummyTrayIcon)
    assert app.tray_icon.visible is True
    assert app.tray_icon.tooltip == 'Voice-controller for OBS'
    
@pytest.mark.usefixtures('patch_freya')
def test_activate_notification_tts(monkeypatch):
    monkeypatch.setattr('freya_app.get_config', lambda: {'notifications': Options.TTS_OPTION.value})
    app = Freya_for_OBS()
    app.activate_notification('Testing TTS')
    assert app.tts_engine.msg == 'Testing TTS'

@pytest.mark.usefixtures('patch_freya')
def test_activate_notification_tray(monkeypatch):
    monkeypatch.setattr('freya_app.get_config', lambda: {'notifications': Options.TRAY_OPTION.value})
    app = Freya_for_OBS()
    app.activate_notification('Tray Msg')
    assert app.tray_icon.msg[1] == 'Tray Msg'

@pytest.mark.usefixtures('patch_freya')
def test_exit(monkeypatch):
    app = Freya_for_OBS()
    app.exit()
    assert app.app.quit_called is True