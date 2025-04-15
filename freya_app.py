import sys
import logging
from yaml_config import load_config
from obs_controller import OBSRecordingController
from voice_recognizer import VoskVoiceRecognizer

from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import QThread, Signal, Slot

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
        
        
    def setup_voice_control(self):
        config = load_config()
        obs_controller = OBSRecordingController(
            host=config['host'],
            port=config['port'],
            password=config['password']
        )
        
        self.voice_thread = QThread()
        
    
    def show_message(self):
        QMessageBox.information(None, "Settings", "Settings will eventually be here")
    
    def run(self):
        self.logger.info('Application started')
        self.app.exec()
    
    def exit(self):
        self.logger.info('Application ended')
        sys.exit(0)