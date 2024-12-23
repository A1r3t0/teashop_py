from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt
from tea_detail_dialog import TeaDetailDialog

class TeaPanel(QWidget):
    def __init__(self, tea, teaShopApp):
        super().__init__()
        self.tea = tea
        self.teaShopApp = teaShopApp
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        imageLabel = QLabel()
        pixmap = QPixmap(f"{self.tea['name']}.png").scaled(200, 200, Qt.KeepAspectRatio)
        imageLabel.setPixmap(pixmap)
        layout.addWidget(imageLabel)

        nameLabel = QLabel(self.tea['name'])
        nameLabel.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(nameLabel)

        priceLabel = QLabel(f"Цена: {self.tea['price']} ₽")
        layout.addWidget(priceLabel)

        buyButton = QPushButton("Купить")
        buyButton.setStyleSheet("background-color: #66CC33; color: white; font: bold 14px;")
        buyButton.clicked.connect(self.showTeaDetail)
        layout.addWidget(buyButton)

        self.setLayout(layout)

    def showTeaDetail(self):
        dialog = TeaDetailDialog(self.tea, self.teaShopApp)
        dialog.exec()
