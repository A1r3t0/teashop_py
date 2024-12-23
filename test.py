import sys
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class ImageTest(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Проверка пути к файлу
        image_path = "logo.png"  # Убедитесь, что путь правильный

        # Загрузка изображения
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            print(f"Ошибка: Не удалось загрузить изображение по пути {image_path}")
        else:
            pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio)
            imageLabel = QLabel()
            imageLabel.setPixmap(pixmap)
            layout.addWidget(imageLabel)

        self.setLayout(layout)
        self.setWindowTitle("Image Test")
        self.setGeometry(100, 100, 200, 200)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageTest()
    window.show()
    sys.exit(app.exec())
