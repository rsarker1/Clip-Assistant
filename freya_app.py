import sys
import logging
import asyncio
from yaml_config import load_config, save_config, get_config
from obs_controller import OBSRecordingController
from voice_recognizer import VoskVoiceRecognizer

from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import QThread, Signal, Slot
from settings_window import SettingsWindow

class VoiceRecognizerThread(QThread):
    error_occured = Signal(str)
    
    def __init__(self, voice_recognizer):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.voice_recognizer = voice_recognizer
        self.exec_loop = None

    def run(self):
        self.exec_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.exec_loop)

        try:
            self.voice_task = self.exec_loop.create_task(self.voice_recognizer.start())
            self.voice_task.add_done_callback(self.on_completion)
            self.exec_loop.run_forever()
        except Exception as e:
            self.logger.error(f'Thread encountered an issue: {e}', exc_info=True)
        finally:
            self.logger.info('Event loop closing. Shutting down thread.')
            self.exec_loop.close()
            
    def on_completion(self, task):
        self.logger.info('Task has been completed')
        try:
            # This re-raises any exception the task had
            task.result()
        except Exception as e:
            self.logger.error(f'Voice recognizer task failed: {e}')
            self.error_occured.emit('Could not connect to OBS. Change connection parameters then try again.')
            self.exec_loop.stop()
            return
                
        if self.exec_loop.is_running():
            self.voice_recognizer.isRunning = False
            self.logger.info('Shutting down voice recognition execution')
            try:
                self.stop_task = self.exec_loop.create_task(self.voice_recognizer.stop())
            except Exception as e:
                self.logger.error(f'Thread encountered an issue: {e}', exc_info=True)
            finally:
                self.exec_loop.call_soon_threadsafe(self.exec_loop.stop)    

    def req_stop(self):
        # Breaks guard clause in voice_recognizer to end task
        self.voice_recognizer.isRunning = False

class Freya_for_OBS:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        self.app = QApplication()
        self.app.setQuitOnLastWindowClosed(False)
        
        self.setup_tray()
        self.setup_voice_control()
    
    def setup_tray(self):
        self.tray_menu = QMenu()
        
        self.settings_action = self.tray_menu.addAction('Settings')
        self.settings_action.triggered.connect(self.show_settings)

        self.exit_action = self.tray_menu.addAction('Exit')
        self.exit_action.triggered.connect(self.exit)
        
        self.tray_icon = QSystemTrayIcon(QIcon('./icons/mic.png'), self.app)
        self.tray_icon.setContextMenu(self.tray_menu)
        
        self.tray_icon.show()
        self.tray_icon.setToolTip('Voice-controller for OBS')
    
    def setup_voice_control(self):
        config = load_config()
        obs_controller = OBSRecordingController(
            host=config['host'],
            port=config['port'],
            password=config['password']
        )

        self.vosk_recognizer = VoskVoiceRecognizer(obs_controller)
        self.voice_thread = VoiceRecognizerThread(self.vosk_recognizer)
        self.voice_thread.error_occured.connect(self.show_error_message)
        self.voice_thread.start()
        
    def show_settings(self):
        self.settings_window = SettingsWindow()
        self.settings_window.obs_settings_updated.connect(self.update_obs_settings)
        self.settings_window.general_settings_updated.connect(self.update_general_settings)
        self.settings_window.show()
    
    @Slot(str, int, str)
    def update_obs_settings(self, host, port, password):
        self.logger.info('Settings updated. Attempting to kill curent thread...')
        self.kill_thread()
        
        changes = {
            'host': host,
            'port': port,
            'password': password
        }
        save_config(get_config(), changes)
        
        self.logger.info('Restarting voice control with new settings...')
        self.setup_voice_control()
        
    @Slot(int, bool)
    def update_general_settings(self, notif, startup):
        self.logger.info('General settings updated')
        
        changes = {
            'notifications': notif,
            'startup': startup
        }
        save_config(get_config(), changes)
        
    @Slot(str)
    def show_error_message(self, msg):
        self.switch_tray_actions(False)
        ok_pressed = QMessageBox.critical(None, 'Error has occured', msg)
        self.tray_icon.showMessage(
            'Voice Recognizer Error',
            msg,
            QSystemTrayIcon.Critical,
            5000 
        )
        if ok_pressed == QMessageBox.StandardButton.Ok:
            self.switch_tray_actions(True)
            self.show_settings()
        
    def switch_tray_actions(self, state):
        self.settings_action.setEnabled(state)
        self.exit_action.setEnabled(state)
        
    def kill_thread(self):
        if self.voice_thread.isRunning():
            self.logger.info('Requesting voice thread to stop...')
            self.voice_thread.req_stop()

        self.voice_thread.wait()
        self.voice_thread.quit()
    
    def run(self):
        self.logger.info('Application started')
        self.app.exec()
    
    def exit(self):
        self.logger.info('Application closing')
        self.kill_thread()
        
        self.logger.info('Done')
        self.app.quit()
        