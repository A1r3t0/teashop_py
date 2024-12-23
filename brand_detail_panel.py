from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PySide6.QtCore import Qt

class BrandDetailPanel(QWidget):
    def __init__(self, brand):
        super().__init__()
        self.brand = brand
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        nameLabel = QLabel(self.brand['name'])
        nameLabel.setFont(QFont("Arial", 24, QFont.Bold))
        nameLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(nameLabel)

        descriptionArea = QTextEdit(self.brand['description'])
        descriptionArea.setReadOnly(True)
        descriptionArea.setFont(QFont("Arial", 14))
        layout.addWidget(descriptionArea)

        self.setLayout(layout)