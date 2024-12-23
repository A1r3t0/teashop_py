from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QScrollArea, QMessageBox
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtCore import Qt
from database_helper import DatabaseHelper

class CartPanel(QWidget):
    def __init__(self, teaShopApp):
        super().__init__()
        self.teaShopApp = teaShopApp
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.cartItemsLayout = QVBoxLayout()
        self.cartItemsLayout.setSpacing(10)

        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollContent = QWidget()
        scrollContent.setLayout(self.cartItemsLayout)
        scrollArea.setWidget(scrollContent)

        summaryPanel = QWidget()
        summaryLayout = QVBoxLayout()

        totalLabel = QLabel("Итого:")
        totalLabel.setFont(QFont("Arial", 16, QFont.Bold))
        summaryLayout.addWidget(totalLabel)

        self.totalPriceLabel = QLabel("0 ₽")
        self.totalPriceLabel.setFont(QFont("Arial", 16, QFont.Bold))
        summaryLayout.addWidget(self.totalPriceLabel)

        checkoutButton = QPushButton("Перейти к оформлению")
        checkoutButton.setStyleSheet("background-color: #66CC33; color: white; font: bold 14px;")
        checkoutButton.clicked.connect(self.checkout)
        summaryLayout.addWidget(checkoutButton)

        summaryPanel.setLayout(summaryLayout)

        self.layout.addWidget(scrollArea)
        self.layout.addWidget(summaryPanel)
        self.setLayout(self.layout)

    def loadCartItems(self):
        # Clear existing items
        while self.cartItemsLayout.count():
            item = self.cartItemsLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Load cart items from the database
        cartItems = DatabaseHelper.getCartItemsByUserId(self.teaShopApp.userId, self.teaShopApp.userRole)
        self.allCartItems = cartItems

        # Display all cart items
        for item in self.allCartItems:
            cartItemWidget = self.createCartItemWidget(item)
            self.cartItemsLayout.addWidget(cartItemWidget)

        self.calculateTotalPrice()

    def createCartItemWidget(self, item):
        cartItemWidget = QWidget()
        cartItemLayout = QHBoxLayout()

        imageLabel = QLabel()
        pixmap = QPixmap(f"{item['name']}.png").scaled(80, 80, Qt.KeepAspectRatio)
        imageLabel.setPixmap(pixmap)
        cartItemLayout.addWidget(imageLabel)

        infoLayout = QVBoxLayout()

        nameLabel = QLabel(item['name'])
        nameLabel.setFont(QFont("Arial", 14, QFont.Bold))
        infoLayout.addWidget(nameLabel)

        priceLabel = QLabel(f"Цена: {item['price']} ₽")
        infoLayout.addWidget(priceLabel)

        quantityLabel = QLabel(f"Количество: {item['quantity']}")
        infoLayout.addWidget(quantityLabel)

        cartItemLayout.addLayout(infoLayout)

        removeButton = QPushButton("Удалить")
        removeButton.setStyleSheet("background-color: red; color: white; font: bold 14px;")
        removeButton.clicked.connect(lambda: self.removeFromCart(item['id'], item['quantity']))
        cartItemLayout.addWidget(removeButton)

        cartItemWidget.setLayout(cartItemLayout)
        cartItemWidget.setStyleSheet("border: 1px solid #ccc; padding: 10px; margin: 5px;")
        return cartItemWidget

    def removeFromCart(self, itemId, quantity):
        try:
            DatabaseHelper.removeFromCart(self.teaShopApp.userId, itemId, quantity)
            self.loadCartItems()  # Обновляем панель корзины после удаления
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при удалении товара из корзины: {str(e)}")

    def calculateTotalPrice(self):
        totalPrice = 0
        for item in self.allCartItems:
            totalPrice += item['quantity'] * item['price'] / 5
        self.totalPriceLabel.setText(f"{totalPrice:.2f} ₽")

    def checkout(self):
        try:
            # Подтверждаем заказ
            DatabaseHelper.confirmOrder(self.teaShopApp.userId, self.teaShopApp.userRole)
            # Очищаем корзину
            DatabaseHelper.clearCart(self.teaShopApp.userId, self.teaShopApp.userRole)
            self.loadCartItems()  # Обновляем панель корзины после очистки
            QMessageBox.information(self, "Оформление заказа", "Заказ успешно оформлен.")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при оформлении заказа: {str(e)}")
