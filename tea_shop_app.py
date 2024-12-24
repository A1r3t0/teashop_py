import sys

from PySide6 import QtGui
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel,
    QPushButton, QLineEdit, QFormLayout, QDialog, QMessageBox, QScrollArea,
    QHBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem, QSpinBox, QFrame,
    QComboBox, QHeaderView
)
from PySide6.QtGui import QPixmap, QFont, QColor
from PySide6.QtCore import Qt
from database_helper import DatabaseHelper
from tea_panel import TeaPanel
from tea_detail_dialog import TeaDetailDialog
from cart_panel import CartPanel  # Импортируем новый класс CartPanel

class TeaShopApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tea Shop")
        self.setGeometry(100, 100, 1200, 800)

        self.userId = 0
        self.userRole = None
        self.allTeas = []

        self.initUI()

    def initUI(self):
        self.tabWidget = QTabWidget()
        self.setCentralWidget(self.tabWidget)

        self.profilePanel = self.createProfilePanel()
        self.catalogPanel = self.createCatalogPanel()
        self.cartPanel = CartPanel(self)  # Используем новый класс CartPanel
        self.ordersPanel = self.createOrdersPanel()  # Создаем панель заказов
        self.adminPanel = self.createAdminPanel()  # Создаем админ-панель

        self.tabWidget.addTab(self.catalogPanel, "Каталог чаев")
        self.tabWidget.addTab(self.ordersPanel, "Мои заказы")  # Добавляем вкладку "Мои заказы"
        self.updateTabsBasedOnRole()  # Обновляем вкладки в зависимости от роли пользователя

        self.tabWidget.currentChanged.connect(self.onTabChanged)

        topPanel = self.createTopPanel()
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(topPanel)
        mainLayout.addWidget(self.tabWidget)

        centralWidget = QWidget()
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

    def createTopPanel(self):
        QtGui.QImageReader.setAllocationLimit(0)
        topPanel = QWidget()
        topLayout = QHBoxLayout()

        logoLabel = QLabel()
        pixmap = QPixmap("logo1.png").scaled(100, 100, Qt.KeepAspectRatio)
        logoLabel.setPixmap(pixmap)
        topLayout.addWidget(logoLabel)

        contactLabel = QLabel("+7 (918) 181-82-55, с 10:00 до 21:00 по МСК")
        contactLabel.setAlignment(Qt.AlignCenter)
        topLayout.addWidget(contactLabel)

        buttonPanel = QWidget()
        buttonLayout = QHBoxLayout()

        personalCabinetButton = QPushButton("Личный кабинет")
        personalCabinetButton.clicked.connect(self.showPersonalCabinet)
        buttonLayout.addWidget(personalCabinetButton)

        if self.userId != 0:  # Проверка, вошел ли пользователь в систему
            logoutButton = QPushButton("Выйти")
            logoutButton.clicked.connect(self.logout)
            buttonLayout.addWidget(logoutButton)

        buttonPanel.setLayout(buttonLayout)
        topLayout.addWidget(buttonPanel)

        topPanel.setLayout(topLayout)
        return topPanel

    def logout(self):
        self.userId = 0
        self.userRole = None
        self.tabWidget.removeTab(self.tabWidget.indexOf(self.profilePanel))
        self.tabWidget.setCurrentIndex(0)
        self.cartPanel.loadCartItems()  # Обновляем корзину после выхода
        self.updateTopPanel()  # Обновляем верхнюю панель после выхода
        self.updateTabsBasedOnRole()  # Обновляем вкладки после выхода
        QMessageBox.information(self, "Выход", "Вы успешно вышли из аккаунта.")

    def showPersonalCabinet(self):
        if self.userId == 0:
            self.showLoginDialog()
        else:
            if self.tabWidget.indexOf(self.profilePanel) == -1:
                self.tabWidget.addTab(self.profilePanel, "Профиль пользователя")
            self.tabWidget.setCurrentWidget(self.profilePanel)
            self.loadUserDataIntoProfile()

    def showLoginDialog(self):
        loginDialog = QDialog(self)
        loginDialog.setWindowTitle("Авторизация")
        loginLayout = QFormLayout()

        emailField = QLineEdit()
        passwordField = QLineEdit()
        passwordField.setEchoMode(QLineEdit.Password)
        statusLabel = QLabel()

        loginLayout.addRow("Email:", emailField)
        loginLayout.addRow("Пароль:", passwordField)

        loginButton = QPushButton("Войти")
        loginButton.clicked.connect(lambda: self.login(emailField.text(), passwordField.text(), statusLabel, loginDialog))
        loginLayout.addRow(loginButton)

        registerButton = QPushButton("Зарегистрироваться")
        registerButton.clicked.connect(lambda: self.showRegisterDialog(loginDialog))
        loginLayout.addRow(registerButton)

        loginLayout.addRow(statusLabel)

        loginDialog.setLayout(loginLayout)
        loginDialog.exec()

    def login(self, email, password, statusLabel, loginDialog):
        user = DatabaseHelper.getUserByEmailAndPassword(email, password)
        if user:
            self.userId = user['id']
            self.userRole = user['role']
            statusLabel.setText("Вход успешен!")
            loginDialog.accept()
            if self.tabWidget.indexOf(self.profilePanel) == -1:
                self.tabWidget.addTab(self.profilePanel, "Профиль пользователя")
            self.tabWidget.setCurrentWidget(self.profilePanel)
            self.loadUserDataIntoProfile()
            self.updateTabsBasedOnRole()
            self.updateTopPanel()  # Обновляем верхнюю панель после входа
        else:
            statusLabel.setText("Неверный email или пароль.")

    def showRegisterDialog(self, loginDialog):
        loginDialog.close()
        registerDialog = QDialog(self)
        registerDialog.setWindowTitle("Регистрация")
        registerLayout = QFormLayout()

        emailField = QLineEdit()
        passwordField = QLineEdit()
        passwordField.setEchoMode(QLineEdit.Password)
        fullNameField = QLineEdit()
        phoneField = QLineEdit()
        statusLabel = QLabel()

        registerLayout.addRow("Email:", emailField)
        registerLayout.addRow("Пароль:", passwordField)
        registerLayout.addRow("Имя:", fullNameField)
        registerLayout.addRow("Телефон:", phoneField)

        registerButton = QPushButton("Зарегистрироваться")
        registerButton.clicked.connect(lambda: self.register(emailField.text(), passwordField.text(), fullNameField.text(), phoneField.text(), statusLabel, registerDialog))
        registerLayout.addRow(registerButton)

        registerLayout.addRow(statusLabel)

        registerDialog.setLayout(registerLayout)
        registerDialog.exec()

    def register(self, email, password, fullName, phone, statusLabel, registerDialog):
        user = DatabaseHelper.registerUser(email, password, fullName, phone)
        if user:
            self.userId = user['id']
            self.userRole = user['role']
            statusLabel.setText("Регистрация успешна!")
            registerDialog.accept()
            if self.tabWidget.indexOf(self.profilePanel) == -1:
                self.tabWidget.addTab(self.profilePanel, "Профиль пользователя")
            self.tabWidget.setCurrentWidget(self.profilePanel)
            self.loadUserDataIntoProfile()
            self.updateTabsBasedOnRole()
            self.updateTopPanel()  # Обновляем верхнюю панель после регистрации
        else:
            statusLabel.setText("Не удалось зарегистрироваться.")

    def createProfilePanel(self):
        profilePanel = QWidget()
        profileLayout = QVBoxLayout()

        profileTitle = QLabel("Профиль пользователя")
        profileTitle.setFont(QFont("Arial", 18, QFont.Bold))
        profileTitle.setAlignment(Qt.AlignCenter)
        profileLayout.addWidget(profileTitle)

        profileFormLayout = QFormLayout()

        self.profileEmailField = QLineEdit()
        self.profileFullNameField = QLineEdit()
        self.profilePhoneField = QLineEdit()

        self.profileEmailField.setStyleSheet("border: 1px solid #ccc; padding: 5px; margin: 5px 0;")
        self.profileFullNameField.setStyleSheet("border: 1px solid #ccc; padding: 5px; margin: 5px 0;")
        self.profilePhoneField.setStyleSheet("border: 1px solid #ccc; padding: 5px; margin: 5px 0;")

        profileFormLayout.addRow("Email:", self.profileEmailField)
        profileFormLayout.addRow("Полное имя:", self.profileFullNameField)
        profileFormLayout.addRow("Телефон:", self.profilePhoneField)

        profileLayout.addLayout(profileFormLayout)

        saveButton = QPushButton("Обновить профиль")
        saveButton.setStyleSheet("background-color: #66CC33; color: white; font: bold 14px; padding: 10px 20px;")
        saveButton.clicked.connect(self.updateUserProfile)
        profileLayout.addWidget(saveButton)

        profilePanel.setLayout(profileLayout)
        return profilePanel

    def updateUserProfile(self):
        fullName = self.profileFullNameField.text()
        phone = self.profilePhoneField.text()
        email = self.profileEmailField.text()

        DatabaseHelper.updateUserProfile(self.userId, fullName, phone)
        DatabaseHelper.updateUserEmail(self.userId, email)
        QMessageBox.information(self, "Успех", "Профиль успешно обновлен.")
        self.loadUserDataIntoProfile()

    def loadUserDataIntoProfile(self):
        user = DatabaseHelper.getUserById(self.userId)
        if user:
            self.profileEmailField.setText(user['email'])
            self.profileFullNameField.setText(user['full_name'])
            self.profilePhoneField.setText(user['phone'])

    def createOrdersPanel(self):
        ordersPanel = QWidget()
        ordersLayout = QVBoxLayout()

        self.ordersTable = QTableWidget()
        self.ordersTable.setColumnCount(3)
        self.ordersTable.setHorizontalHeaderLabels(["ID", "Дата", "Статус"])
        self.ordersTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        ordersLayout.addWidget(self.ordersTable)

        ordersPanel.setLayout(ordersLayout)
        return ordersPanel

    def loadUserOrders(self):
        orders = DatabaseHelper.getUserOrders(self.userId)
        self.ordersTable.setRowCount(len(orders))
        for row, order in enumerate(orders):
            self.ordersTable.setItem(row, 0, QTableWidgetItem(str(order['id'])))
            self.ordersTable.setItem(row, 1, QTableWidgetItem(order['order_date'].strftime("%Y-%m-%d %H:%M:%S")))
            self.ordersTable.setItem(row, 2, QTableWidgetItem(order['status']))

    def createAdminPanel(self):
        adminPanel = QWidget()
        adminLayout = QVBoxLayout()

        self.adminOrdersTable = QTableWidget()
        self.adminOrdersTable.setColumnCount(4)
        self.adminOrdersTable.setHorizontalHeaderLabels(["ID", "Дата", "Статус", "Действие"])
        self.adminOrdersTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        adminLayout.addWidget(self.adminOrdersTable)

        addTeaButton = QPushButton("Добавить чай")
        addTeaButton.clicked.connect(self.showAddTeaDialog)
        adminLayout.addWidget(addTeaButton)

        adminPanel.setLayout(adminLayout)
        return adminPanel

    def showAddTeaDialog(self):
        addTeaDialog = QDialog(self)
        addTeaDialog.setWindowTitle("Добавить чай")
        addTeaLayout = QFormLayout()

        nameField = QLineEdit()
        brandField = QComboBox()
        supplierField = QComboBox()
        priceField = QLineEdit()
        stockField = QLineEdit()
        imagePathField = QLineEdit()  # Поле для ввода пути к фотографии чая

        brands = DatabaseHelper.getAllBrands()
        suppliers = DatabaseHelper.getAllSuppliers()

        for brand in brands:
            brandField.addItem(brand['name'], brand['id'])

        for supplier in suppliers:
            supplierField.addItem(supplier['contact_info'], supplier['id'])

        addTeaLayout.addRow("Название:", nameField)
        addTeaLayout.addRow("Бренд:", brandField)
        addTeaLayout.addRow("Поставщик:", supplierField)
        addTeaLayout.addRow("Цена:", priceField)
        addTeaLayout.addRow("Количество:", stockField)
        addTeaLayout.addRow("Путь к фотографии:", imagePathField)  # Добавляем поле для ввода пути к фотографии чая

        addButton = QPushButton("Добавить")
        addButton.clicked.connect(
            lambda: self.addTea(nameField.text(), brandField.currentData(), supplierField.currentData(),
                                priceField.text(), stockField.text(), imagePathField.text(), addTeaDialog))
        addTeaLayout.addRow(addButton)

        addTeaDialog.setLayout(addTeaLayout)
        addTeaDialog.exec()

    def addTea(self, name, brandId, supplierId, price, stock, imagePath, addTeaDialog):
        try:
            price = float(price)
            stock = int(stock)
            DatabaseHelper.addTea(name, brandId, supplierId, price, stock, imagePath)
            addTeaDialog.accept()
            self.loadTeas()  # Обновляем каталог чаев
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Неверные данные. Пожалуйста, проверьте введенные значения.")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при добавлении чая: {str(e)}")

    def loadAdminOrders(self):
        orders = DatabaseHelper.getAllOrders()
        self.adminOrdersTable.setRowCount(len(orders))
        for row, order in enumerate(orders):
            self.adminOrdersTable.setItem(row, 0, QTableWidgetItem(str(order['id'])))
            self.adminOrdersTable.setItem(row, 1, QTableWidgetItem(order['order_date'].strftime("%Y-%m-%d %H:%M:%S")))
            self.adminOrdersTable.setItem(row, 2, QTableWidgetItem(order['status']))

            statusComboBox = QComboBox()
            statusComboBox.addItems(["В ожидании", "Подтверждено", "Отклонено", "Доставлено", "В пути", "Отправлено"])
            statusComboBox.setCurrentText(order['status'])
            statusComboBox.currentTextChanged.connect(lambda text, orderId=order['id']: self.updateOrderStatus(orderId, text))
            self.adminOrdersTable.setCellWidget(row, 3, statusComboBox)

    def updateOrderStatus(self, orderId, status):
        DatabaseHelper.updateOrderStatus(orderId, status)
        QMessageBox.information(self, "Успех", f"Статус заказа {orderId} обновлен.")

    def createCatalogPanel(self):
        catalogPanel = QWidget()
        catalogLayout = QVBoxLayout()

        self.teaGrid = QGridLayout()
        self.teaGrid.setSpacing(10)

        self.loadTeas()

        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollContent = QWidget()
        scrollContent.setLayout(self.teaGrid)
        scrollArea.setWidget(scrollContent)

        catalogLayout.addWidget(scrollArea)
        catalogPanel.setLayout(catalogLayout)
        return catalogPanel

    def loadTeas(self):
        self.allTeas = DatabaseHelper.getAllTeas(self.userRole)
        self.displayTeas()

    def displayTeas(self):
        # Очищаем текущие виджеты
        while self.teaGrid.count():
            item = self.teaGrid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        row = 0
        col = 0
        for i, tea in enumerate(self.allTeas):
            teaPanel = TeaPanel(tea, self)
            self.teaGrid.addWidget(teaPanel, row, col)
            col += 1
            if col == 3:
                col = 0
                row += 1

    def onTabChanged(self, index):
        if index == self.tabWidget.indexOf(self.cartPanel) or index == self.tabWidget.indexOf(self.ordersPanel):
            if self.userId == 0:
                self.showLoginDialog()
                self.tabWidget.setCurrentIndex(0)  # Возвращаемся на первую вкладку
                return

        if index == self.tabWidget.indexOf(self.cartPanel):
            self.cartPanel.loadCartItems()
        elif index == self.tabWidget.indexOf(self.ordersPanel):
            self.loadUserOrders()
        elif index == self.tabWidget.indexOf(self.adminPanel):
            self.loadAdminOrders()

    def updateTabsBasedOnRole(self):
        if self.userRole == "admin":
            if self.tabWidget.indexOf(self.adminPanel) == -1:
                self.tabWidget.addTab(self.adminPanel, "Админ-панель")
            self.tabWidget.removeTab(self.tabWidget.indexOf(self.cartPanel))
        else:
            if self.tabWidget.indexOf(self.cartPanel) == -1:
                self.tabWidget.addTab(self.cartPanel, "Корзина")
            self.tabWidget.removeTab(self.tabWidget.indexOf(self.adminPanel))

    def updateTopPanel(self):
        topPanel = self.createTopPanel()
        mainLayout = self.centralWidget().layout()
        oldTopPanel = mainLayout.itemAt(0).widget()
        mainLayout.replaceWidget(oldTopPanel, topPanel)
        oldTopPanel.deleteLater()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TeaShopApp()
    window.show()
    sys.exit(app.exec())