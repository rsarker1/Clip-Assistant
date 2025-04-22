from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Signal

class ErrorModal(QWidget):
    
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Error')
        
        layout = QVBoxLayout()