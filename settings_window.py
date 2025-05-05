from yaml_config import get_config
from enums import Options

from PySide6.QtWidgets import ( 
    QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, 
    QPushButton, QTabWidget, QComboBox, QCheckBox 
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal

class SettingsWindow(QWidget):
    obs_settings_updated = Signal(str, int, str)
    general_settings_updated = Signal(str, bool)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Settings')
        self.setWindowIcon(QIcon('./icons/settings.png'))
        self.setMinimumSize(400, 300)
        self.setMaximumSize(600, 400)
        
        self.config = get_config()
        
        self.tabs = QTabWidget(self)
        self.setup_general_tab()
        self.setup_OBS_tab()
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        
        self.setLayout(main_layout)
        
    def setup_general_tab(self):
        general_tab = QWidget()
        general_layout = QFormLayout()
        options = [Options.TTS_OPTION.value, Options.TRAY_OPTION.value, Options.NONE_OPTION.value]
        
        general_layout.addRow(QLabel('Select Notification Type:'))
        self.notif_dropdown = QComboBox()
        self.notif_dropdown.addItems(options)
        self.notif_dropdown.setCurrentIndex(options.index(self.config.get('notifications')))
        self.notif_dropdown.currentIndexChanged.connect(self.save_general_settings)
        general_layout.addRow(self.notif_dropdown)
        
        general_layout.addRow(QLabel(''))
        
        self.startup_checkbox = QCheckBox('Run on startup')
        self.startup_checkbox.setChecked(self.config.get('startup'))
        self.startup_checkbox.stateChanged.connect(self.save_general_settings)
        general_layout.addRow(self.startup_checkbox)
        
        general_tab.setLayout(general_layout)
        self.tabs.addTab(general_tab, 'General')
        
    def setup_OBS_tab(self):    
        obs_tab = QWidget()
        obs_layout = QVBoxLayout()
        
        self.host_input = QLineEdit()
        self.port_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        obs_layout.addWidget(QLabel('Host:'))
        obs_layout.addWidget(self.host_input)
        obs_layout.addWidget(QLabel('Port:'))
        obs_layout.addWidget(self.port_input)
        obs_layout.addWidget(QLabel('Password:'))
        obs_layout.addWidget(self.password_input)
        
        self.error_label = QLabel('')
        self.error_label.setStyleSheet('color: red')
        obs_layout.addWidget(self.error_label)
        
        save_button = QPushButton('Save')
        save_button.clicked.connect(self.save_obs_settings)
        obs_layout.addWidget(save_button)
        
        obs_tab.setLayout(obs_layout)
        self.tabs.addTab(obs_tab, 'OBS')
        
    def save_obs_settings(self):
        self.error_label.setText('')
        
        host = self.host_input.text().strip()
        port = self.port_input.text().strip()
        password = self.password_input.text().strip()
            
        if not host or not port or not password:
            self.error_label.setText('Error: Empty text not allowed')
            return

        try:
            port = int(port)
        except ValueError:
            self.error_label.setText('Error: Port must be an integer')
            return
        
        self.obs_settings_updated.emit(host, port, password)
        self.close()
        
    def save_general_settings(self):
        notif = self.notif_dropdown.currentText()
        startup = self.startup_checkbox.isChecked()
        
        self.general_settings_updated.emit(notif, startup)