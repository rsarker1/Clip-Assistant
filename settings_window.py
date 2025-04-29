from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Signal

class SettingsWindow(QWidget):
    settings_updated = Signal(str, int, str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Settings')
        self.setFixedSize(300, 250)
        
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
        
        self.error_label = QLabel('')
        self.error_label.setStyleSheet('color: red')
        layout.addWidget(self.error_label)
        
        save_button = QPushButton('Save')
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)
        
        self.setLayout(layout)
        
    def save_settings(self):
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
        
        self.settings_updated.emit(host, port, password)
        self.close()