from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QComboBox, QHBoxLayout, QMessageBox
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt
from database_helper import DatabaseHelper

class TeaDetailDialog(QDialog):
    def __init__(self, tea, teaShopApp):
        super().__init__()
        self.tea = tea
        self.teaShopApp = teaShopApp
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Информация о чае")
        self.setGeometry(300, 200, 400, 300)

        layout = QVBoxLayout()

        imageLabel = QLabel()
        pixmap = QPixmap(f"{self.tea['name']}.png").scaled(200, 200, Qt.KeepAspectRatio)
        imageLabel.setPixmap(pixmap)
        layout.addWidget(imageLabel)

        nameLabel = QLabel(self.tea['name'])
        nameLabel.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(nameLabel)

        brand = DatabaseHelper.getBrandById(self.tea['brand_id'])
        supplier = DatabaseHelper.getSupplierById(self.tea['supplier_id'])

        brandLabel = QLabel(f"Бренд: {brand['name']}")
        layout.addWidget(brandLabel)

        supplierLabel = QLabel(f"Поставщик: {supplier['contact_info']}")
        layout.addWidget(supplierLabel)

        priceLabel = QLabel(f"Цена: {self.tea['price']} ₽")
        layout.addWidget(priceLabel)

        quantityLabel = QLabel("Количество:")
        layout.addWidget(quantityLabel)

        self.quantityComboBox = QComboBox()
        quantities = self.generateQuantityOptions(self.tea['stock'])
        self.quantityComboBox.addItems(quantities)
        layout.addWidget(self.quantityComboBox)

        buyButton = QPushButton("Купить")
        buyButton.setStyleSheet("background-color: #66CC33; color: black; font: bold 14px;")
        buyButton.clicked.connect(self.buyTea)
        layout.addWidget(buyButton)

        self.setLayout(layout)

    def generateQuantityOptions(self, stock):
        availableQuantities = [5, 25, 50, 100]
        quantities = [str(q) + " г" for q in availableQuantities if q <= stock]
        if stock not in availableQuantities:
            quantities.append(str(stock) + " г")
        return quantities

    def buyTea(self):
        if self.teaShopApp.userId == 0:
            self.teaShopApp.showLoginDialog()
        else:
            selectedQuantity = self.quantityComboBox.currentText()
            quantityInGrams = int(selectedQuantity.replace(" г", ""))
            currentStock = DatabaseHelper.getTeaStock(self.tea['id'])
            if quantityInGrams <= currentStock:
                DatabaseHelper.addToCart(self.teaShopApp.userId, self.tea['id'], quantityInGrams)
                QMessageBox.information(self, "Успех", "Чай добавлен в корзину.")
                self.teaShopApp.updateCartPanel()
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Недостаточно чая на складе.")
