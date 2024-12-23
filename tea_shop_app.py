import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel,
    QPushButton, QLineEdit, QFormLayout, QDialog, QMessageBox, QScrollArea,
    QHBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem, QSpinBox, QFrame
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
        self.itemsPerPage = 9
        self.currentPage = 1

        self.initUI()

    def initUI(self):
        self.tabWidget = QTabWidget()
        self.setCentralWidget(self.tabWidget)

        self.profilePanel = self.createProfilePanel()
        self.catalogPanel = self.createCatalogPanel()
        self.cartPanel = CartPanel(self)  # Используем новый класс CartPanel
        self.ordersPanel = self.createOrdersPanel()  # Создаем панель заказов

        self.tabWidget.addTab(self.catalogPanel, "Каталог чаев")
        self.tabWidget.addTab(self.cartPanel, "Корзина")
        self.tabWidget.addTab(self.ordersPanel, "Мои заказы")  # Добавляем новую вкладку

        self.tabWidget.currentChanged.connect(self.onTabChanged)

        topPanel = self.createTopPanel()
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(topPanel)
        mainLayout.addWidget(self.tabWidget)

        centralWidget = QWidget()
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

    def createTopPanel(self):
        topPanel = QWidget()
        topLayout = QHBoxLayout()

        logoLabel = QLabel()
        pixmap = QPixmap("logo.png").scaled(80, 80, Qt.KeepAspectRatio)
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
        else:
            statusLabel.setText("Не удалось зарегистрироваться.")

    def createProfilePanel(self):
        profilePanel = QWidget()
        profileLayout = QVBoxLayout()

        self.profileEmailField = QLineEdit()
        self.profileFullNameField = QLineEdit()
        self.profilePhoneField = QLineEdit()

        profileLayout.addWidget(QLabel("Профиль пользователя"))
        profileLayout.addWidget(self.profileEmailField)
        profileLayout.addWidget(self.profileFullNameField)
        profileLayout.addWidget(self.profilePhoneField)

        saveButton = QPushButton("Обновить профиль")
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

        paginationPanel = QWidget()
        paginationLayout = QHBoxLayout()

        prevButton = QPushButton("Предыдущая")
        prevButton.clicked.connect(self.prevPage)
        nextButton = QPushButton("Следующая")
        nextButton.clicked.connect(self.nextPage)

        paginationLayout.addWidget(prevButton)
        paginationLayout.addWidget(nextButton)
        paginationPanel.setLayout(paginationLayout)

        catalogLayout.addWidget(scrollArea)
        catalogLayout.addWidget(paginationPanel)
        catalogPanel.setLayout(catalogLayout)
        return catalogPanel

    def loadTeas(self):
        self.allTeas = DatabaseHelper.getAllTeas(self.userRole)
        self.displayPage()

    def displayPage(self):
        startIndex = (self.currentPage - 1) * self.itemsPerPage
        endIndex = min(startIndex + self.itemsPerPage, len(self.allTeas))

        for i in range(self.teaGrid.count()):
            self.teaGrid.itemAt(i).widget().setParent(None)

        for i in range(startIndex, endIndex):
            tea = self.allTeas[i]
            teaPanel = TeaPanel(tea, self)
            self.teaGrid.addWidget(teaPanel, (i - startIndex) // 3, (i - startIndex) % 3)

    def prevPage(self):
        if self.currentPage > 1:
            self.currentPage -= 1
            self.displayPage()

    def nextPage(self):
        if self.currentPage < self.getTotalPages():
            self.currentPage += 1
            self.displayPage()

    def getTotalPages(self):
        return (len(self.allTeas) + self.itemsPerPage - 1) // self.itemsPerPage

    def onTabChanged(self, index):
        if index == self.tabWidget.indexOf(self.cartPanel):
            self.cartPanel.loadCartItems()
        elif index == self.tabWidget.indexOf(self.ordersPanel):
            self.loadUserOrders()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TeaShopApp()
    window.show()
    sys.exit(app.exec())
