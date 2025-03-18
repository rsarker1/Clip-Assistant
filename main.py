import asyncio
import logging
import sys
from datetime import datetime
from yaml_config import load_config
from obs_controller import OBSRecordingController
from voice_recognizer import VoskVoiceRecognizer

from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QThread, Signal, Slot, Qt

class Freya_for_OBS:
    def __init__(self):
        self.app = QApplication()
        self.app.setQuitOnLastWindowClosed(False)
        
        self.tray_icon = QSystemTrayIcon(QIcon('./mic.png'), self.app)
        
        self.create_context_menu()
        
        self.tray_icon.setContextMenu(self.tray_menu)
        
        self.tray_icon.show()
        self.tray_icon.setToolTip('Voice-controller for OBS')
        
    def create_context_menu(self):
        tray_menu = QMenu()
        
        show_message_action = tray_menu.addAction('Show Message')
        show_message_action.triggered.connect(self.show_message)

        exit_action = tray_menu.addAction('Exit')
        exit_action.triggered.connect(self.exit)
        
        self.tray_menu = tray_menu
        
    def show_message(self):
        QMessageBox.information(None, "Hello", "Test box")
    
    def run(self):
        self.app.exec()
    
    def exit(self):
        sys.exit()
        

def setup_logging():
    log_file = logging.getLogger(__name__)
    current_date = datetime.today().strftime('%Y_%m_%d')
    logging.basicConfig(
        filename=f'clip_assistant_{current_date}.log', 
        filemode='w', 
        format='%(asctime)s:[%(levelname)s]:(%(name)s):%(message)s',
        datefmt='%H:%M:%S',
        level=logging.INFO
    )
    return log_file

async def main():
    logger = setup_logging()
    logger.info('Started')
    
    config = load_config()
    obs_controller = OBSRecordingController(
        host=config['host'],
        port=config['port'],
        password=config['password']
    )
    
    app = Freya_for_OBS() 
    app.run()
    
    # voice_recognize = VoskVoiceRecognizer(obs_controller)
    # try:
    #     await voice_recognize.start()
    # except KeyboardInterrupt:
    #     await voice_recognize.stop()
    #     sys.exit(0)    
    # finally:
    #     logger.info('Ended')
    
asyncio.run(main())
