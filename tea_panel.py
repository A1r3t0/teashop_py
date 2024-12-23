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

        nameLabel = QLabel(self.tea['name'])
        nameLabel.setFont(QFont("Arial", 16, QFont.Bold))
        nameLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(nameLabel)

        imageLabel = QLabel()
        pixmap = QPixmap(self.tea['image_path']).scaled(200, 200, Qt.KeepAspectRatio)
        imageLabel.setPixmap(pixmap)
        imageLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(imageLabel)

        priceLabel = QLabel(f"Цена: {self.tea['price']} ₽ / 5 г")
        priceLabel.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(priceLabel)

        if self.teaShopApp.userRole == "admin":
            orderButton = QPushButton("Заказать")
            orderButton.setStyleSheet("background-color: #66CC33; color: white; font: bold 14px;")
            orderButton.clicked.connect(self.showOrderTeaDialog)
            layout.addWidget(orderButton)
        else:
            buyButton = QPushButton("Купить")
            buyButton.setStyleSheet("background-color: #66CC33; color: white; font: bold 14px;")
            buyButton.clicked.connect(self.showTeaDetail)
            layout.addWidget(buyButton)

        self.setLayout(layout)
        self.setFixedSize(220, 300)  # Устанавливаем фиксированный размер для панели чая

    def showTeaDetail(self):
        dialog = TeaDetailDialog(self.tea, self.teaShopApp)
        dialog.exec()

    def showOrderTeaDialog(self):
        dialog = TeaDetailDialog(self.tea, self.teaShopApp)
        dialog.exec()