import sys
import logging
import asyncio
from yaml_config import load_config
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
            self.logger.info('Event loop closing')
            self.exec_loop.close()
            
    def on_completion(self, task):
        self.logger.info('IN THE CALLBACK')
        try:
            # This re-raises any exception the task had
            task.result()
        except Exception as e:
            self.logger.error(f'Voice recognizer task failed: {e}')
            self.error_occured.emit('DAMN')
            self.logger.info('Voice recognizer task finished, stopping event loop')
            self.exec_loop.stop()
            return
            
        if not self.voice_task.done():
            print('TASK IS STILL RUNNING')
        if self.voice_task.done():
            print('TASK IS DEAD')
        
        if self.exec_loop.is_running():
            print('Loop running')
        else:
            print('Loop not running')
        
        if self.exec_loop.is_running():
            self.voice_recognizer.isRunning = False
            self.logger.info('Shutting down voice recognition execution')
            try:
                self.stop_task = self.exec_loop.create_task(self.voice_recognizer.stop())
            except Exception as e:
                self.logger.error(f'Thread encountered an issue: {e}', exc_info=True)
            finally:
                self.exec_loop.call_soon_threadsafe(self.exec_loop.stop)
                # self.exec_loop.stop()
                
                
            # future = asyncio.run_coroutine_threadsafe(self.voice_recognizer.stop(), self.exec_loop)
            # try:
            #     future.result(timeout=5)
            # except Exception as e:
            #     self.logger.error(f'Thread encountered issue on stop(): {e}', exc_info=True)
            # finally:
            #     self.exec_loop.call_soon_threadsafe(self.exec_loop.stop)
        else:
            self.logger.info('Did not run')     
            
        # self.logger.info('Voice recognizer task finished, stopping event loop')
        # self.exec_loop.stop()
        
    def req_stop(self):
        self.voice_recognizer.isRunning = False
        # if not self.voice_task.done():
        #     print('TASK IS STILL RUNNING')
        # if self.voice_task.done():
        #     print('TASK IS DEAD')
        
        # if self.exec_loop.is_running():
        #     print('Loop running')
        # else:
        #     print('Loop not running')
        
        # if self.exec_loop.is_running():
        #     self.voice_recognizer.isRunning = False
        #     self.logger.info('Shutting down voice recognition execution')

        #     future = asyncio.run_coroutine_threadsafe(self.voice_recognizer.stop(), self.exec_loop)
        #     try:
        #         future.result(timeout=5)
        #     except Exception as e:
        #         self.logger.error(f'Thread encountered issue on stop(): {e}', exc_info=True)
        #     finally:
        #         self.exec_loop.call_soon_threadsafe(self.exec_loop.stop)
        # else:
        #     self.logger.info('Did not run')

        
class Freya_for_OBS:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        self.app = QApplication()
        self.app.setQuitOnLastWindowClosed(False)
        
        self.tray_menu = QMenu()
        
        settings_action = self.tray_menu.addAction('Settings')
        settings_action.triggered.connect(self.show_settings)

        exit_action = self.tray_menu.addAction('Exit')
        exit_action.triggered.connect(self.exit)
        
        self.tray_icon = QSystemTrayIcon(QIcon('./icons/mic.png'), self.app)
        self.tray_icon.setContextMenu(self.tray_menu)
        
        self.tray_icon.show()
        self.tray_icon.setToolTip('Voice-controller for OBS')
        
        self.setup_voice_control()
        
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

    @Slot(str)
    def show_error_message(self, msg):
        ok_pressed = QMessageBox.critical(None, 'Error has occured', msg)
        print(ok_pressed)
        self.exit()
        # Exit app on 'Ok' button pressed. Should notify user how to fix based on different errors
        
    def show_settings(self):
        self.settings_window = SettingsWindow()
        self.settings_window.settings_updated.connect(self.save_settings)
        self.settings_window.show()
    
    @Slot(str, int, str)
    def save_settings(self, host, port, password):
        self.logger.info(f'Settings updated: host={host}, port={port}')
    
    def run(self):
        self.logger.info('Application started')
        self.app.exec()
    
    def exit(self):
        self.logger.info('Application closing')
        if self.voice_thread.isRunning():
            print('Voice thread running')
        else:
            print('Thread not running')
            
        if self.voice_thread.isRunning():
            self.logger.info('Requesting voice thread to stop...')
            self.voice_thread.req_stop()

        self.voice_thread.wait()
        self.voice_thread.quit()
        
        self.logger.info('Done')
        self.app.quit()
        