from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QComboBox, QHBoxLayout, QMessageBox
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt
from database_helper import DatabaseHelper
from brand_detail_panel import BrandDetailPanel  # Импортируем новый класс BrandDetailPanel

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
        image_path = self.tea.get('image_path', 'default_image.png')  # Используем запасное изображение, если image_path не установлен
        pixmap = QPixmap(image_path).scaled(200, 200, Qt.KeepAspectRatio)
        imageLabel.setPixmap(pixmap)
        layout.addWidget(imageLabel)

        nameLabel = QLabel(self.tea['name'])
        nameLabel.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(nameLabel)

        brand = DatabaseHelper.getBrandById(self.tea['brand_id'])
        supplier = DatabaseHelper.getSupplierById(self.tea['supplier_id'])

        # Создаем QLabel для бренда с кастомным стилем
        brandLabel = QLabel(f"Бренд: {brand['name']}")
        brandLabel.setStyleSheet("color: blue;")
        brandLabel.mousePressEvent = lambda event: self.showBrandDetail(brand)  # Добавляем обработчик события клика
        layout.addWidget(brandLabel)

        # Создаем QLabel для поставщика с кастомным стилем
        supplierLabel = QLabel(f"Поставщик: {supplier['name']}")
        supplierLabel.setStyleSheet("color: blue;")
        supplierLabel.mousePressEvent = lambda event: self.showSupplierDetail(supplier)  # Добавляем обработчик события клика
        layout.addWidget(supplierLabel)

        self.priceLabel = QLabel(f"Цена: {self.tea['price']} ₽")
        layout.addWidget(self.priceLabel)

        quantityLabel = QLabel("Количество:")
        layout.addWidget(quantityLabel)

        self.quantityComboBox = QComboBox()
        quantities = self.generateQuantityOptions(self.tea['stock'])
        self.quantityComboBox.addItems(quantities)
        self.quantityComboBox.currentIndexChanged.connect(self.updatePrice)  # Добавляем обработчик события изменения выбранного количества
        layout.addWidget(self.quantityComboBox)

        if self.teaShopApp.userRole == "admin":
            orderButton = QPushButton("Заказать")
            orderButton.setStyleSheet("background-color: #66CC33; color: black; font: bold 14px;")
            orderButton.clicked.connect(self.orderTea)
        else:
            buyButton = QPushButton("Купить")
            buyButton.setStyleSheet("background-color: #66CC33; color: black; font: bold 14px;")
            buyButton.clicked.connect(self.buyTea)
        layout.addWidget(orderButton if self.teaShopApp.userRole == "admin" else buyButton)

        self.setLayout(layout)

    def showBrandDetail(self, brand):
        brandDetailDialog = QDialog(self)
        brandDetailDialog.setWindowTitle("Информация о бренде")
        brandDetailDialog.setGeometry(300, 200, 400, 300)

        brandDetailPanel = BrandDetailPanel(brand)
        brandDetailLayout = QVBoxLayout()
        brandDetailLayout.addWidget(brandDetailPanel)

        brandDetailDialog.setLayout(brandDetailLayout)
        brandDetailDialog.exec()

    def showSupplierDetail(self, supplier):
        supplierDetailDialog = QDialog(self)
        supplierDetailDialog.setWindowTitle("Информация о поставщике")
        supplierDetailDialog.setGeometry(300, 200, 400, 300)

        supplierDetailLayout = QVBoxLayout()

        nameLabel = QLabel(supplier['name'])
        nameLabel.setFont(QFont("Arial", 24, QFont.Bold))
        nameLabel.setAlignment(Qt.AlignCenter)
        supplierDetailLayout.addWidget(nameLabel)

        contactInfoLabel = QLabel(f"Контактная информация: {supplier['contact_info']}")
        supplierDetailLayout.addWidget(contactInfoLabel)

        createdYearLabel = QLabel(f"Год создания: {supplier['created_year']}")
        supplierDetailLayout.addWidget(createdYearLabel)

        supplierDetailDialog.setLayout(supplierDetailLayout)
        supplierDetailDialog.exec()

    def generateQuantityOptions(self, stock):
        if self.teaShopApp.userRole == "admin":
            return ["100 г", "250 г", "500 г", "750 г", "1000 г"]
        else:
            availableQuantities = [5, 25, 50, 100]
            quantities = [str(q) + " г" for q in availableQuantities if q <= stock]
            if stock not in availableQuantities:
                quantities.append(str(stock) + " г")
            return quantities

    def updatePrice(self, index):
        selectedQuantity = self.quantityComboBox.currentText()
        quantityInGrams = int(selectedQuantity.replace(" г", ""))
        totalPrice = self.tea['price'] * (quantityInGrams) / 5  # Предполагаем, что цена указана за килограмм
        self.priceLabel.setText(f"Цена: {totalPrice:.2f} ₽")

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

    def orderTea(self):
        selectedQuantity = self.quantityComboBox.currentText()
        quantityInGrams = int(selectedQuantity.replace(" г", ""))
        DatabaseHelper.addToAdminOrder(self.teaShopApp.userId, self.tea['id'], quantityInGrams)
        QMessageBox.information(self, "Успех", "Чай добавлен в заказ администратора.")
        self.accept()
