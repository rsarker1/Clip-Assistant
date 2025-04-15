import sys
import logging
import asyncio
from yaml_config import load_config
from obs_controller import OBSRecordingController
from voice_recognizer import VoskVoiceRecognizer

from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import QThread, Signal, Slot


class VoiceRecognizerThread(QThread):
    def __init__(self, voice_recognizer):
        super().__init__()
        self.voice_recognizer = voice_recognizer
        self.exec_loop = None

    def run(self):
        self.exec_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.exec_loop)

        try:
            self.voice_task = self.exec_loop.create_task(self.voice_recognizer.start())
            self.exec_loop.run_forever()
        except Exception as e:
            logging.error(f"Error in voice recognition thread: {e}", exc_info=True)
        finally:
            # Clean up any pending tasks
            pending = asyncio.all_tasks(loop=self.exec_loop)
            if pending:
                self.exec_loop.run_until_complete(
                    asyncio.gather(*pending, return_exceptions=True)
                )
            self.exec_loop.close()
            logging.info("Voice recognition thread event loop closed")
        
class Freya_for_OBS:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        self.app = QApplication()
        self.app.setQuitOnLastWindowClosed(False)
        
        self.tray_menu = QMenu()
        
        show_message_action = self.tray_menu.addAction('Settings')
        show_message_action.triggered.connect(self.show_message)

        exit_action = self.tray_menu.addAction('Exit')
        exit_action.triggered.connect(self.exit)
        
        self.tray_icon = QSystemTrayIcon(QIcon('./mic.png'), self.app)
        self.tray_icon.setContextMenu(self.tray_menu)
        
        self.tray_icon.show()
        self.tray_icon.setToolTip('Voice-controller for OBS')
        
        self.setup_voice_control()
        
    def setup_app_interface(self):
        return
        
    def setup_voice_control(self):
        config = load_config()
        obs_controller = OBSRecordingController(
            host=config['host'],
            port=config['port'],
            password=config['password']
        )
        
        self.vosk_recognizer = VoskVoiceRecognizer(obs_controller)
        
        self.voice_thread = VoiceRecognizerThread(self.vosk_recognizer)
        self.voice_thread.start()
        
    def show_message(self):
        QMessageBox.information(None, "Settings", "Settings will eventually be here")
    
    def run(self):
        self.logger.info('Application started')
        self.app.exec()
    
    def exit(self):
        # self.logger.info('Application ended')
        if self.voice_thread.isRunning():
            self.logger.info('Thread running')
            if self.voice_thread.exec_loop:
                voice_future = asyncio.run_coroutine_threadsafe(self.vosk_recognizer.stop(), self.voice_thread.exec_loop)
                
                try: 
                    voice_future.result(timeout=5)
                except Exception as e:
                    self.logger.info(f'Error waiting for stop(): {e}', exc_info=True)
                    
                self.voice_thread.exec_loop.call_soon_threadsafe(self.voice_thread.exec_loop.stop)
        
        # self.voice_thread.wait()
        self.voice_thread.quit()
        self.app.quit()