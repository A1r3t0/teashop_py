from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QMessageBox
from PySide6.QtCore import Qt
from database_helper import DatabaseHelper

class CartItemPanel(QWidget):
    def __init__(self, cartItem, teaShopApp):
        super().__init__()
        self.cartItem = cartItem
        self.teaShopApp = teaShopApp
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()

        imageLabel = QLabel("Изображение чая")
        imageLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(imageLabel)

        infoLayout = QVBoxLayout()

        nameLabel = QLabel(self.cartItem['name'])
        nameLabel.setFont(QFont("Arial", 16, QFont.Bold))
        infoLayout.addWidget(nameLabel)

        priceLabel = QLabel(f"Цена: {self.cartItem['price']} ₽")
        priceLabel.setFont(QFont("Arial", 14))
        infoLayout.addWidget(priceLabel)

        quantityLabel = QLabel(f"Количество: {self.cartItem['quantity']}")
        infoLayout.addWidget(quantityLabel)

        layout.addLayout(infoLayout)

        removeButton = QPushButton("Удалить")
        removeButton.setStyleSheet("background-color: red; color: white; font: bold 14px;")
        removeButton.clicked.connect(self.removeFromCart)
        layout.addWidget(removeButton)

        self.setLayout(layout)

    def removeFromCart(self):
        try:
            DatabaseHelper.removeFromCart(self.teaShopApp.userId, self.cartItem['id'], self.cartItem['quantity'])
            self.teaShopApp.updateCartPanel()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", "Ошибка при удалении чая из корзины.")
