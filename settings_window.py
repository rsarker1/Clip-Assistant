from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Signal

class SettingsWindow(QWidget):
    settings_updated = Signal(str, int, str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Settings')
        
        layout = QVBoxLayout()
        
        self.host_input = QLineEdit()
        self.port_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        layout.addWidget(QLabel('Host:'))
        layout.addWidget(self.host_input)
        layout.addWidget(QLabel('Port:'))
        layout.addWidget(self.port_input)
        layout.addWidget(QLabel('Password:'))
        layout.addWidget(self.password_input)
        
        save_button = QPushButton('Save')
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)
        
        self.setLayout(layout)
        
    def save_settings(self):
        host = self.host_input.text()
        port = int(self.port_input.text())
        password = self.password_input.text()
        self.settings_updated.emit(host, port, password)
        self.close()