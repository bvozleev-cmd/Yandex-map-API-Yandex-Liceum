import sys
import requests
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QWidget, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

API_KEY = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"
SERVER = "https://static-maps.yandex.ru/v1?"

MIN_SPN = 0.0005
MAX_SPN = 50
ZOOM_STEP = 2


class MapWindow(QMainWindow):
    def __init__(self, lon, lat, spn):
        super().__init__()

        self.lon = float(lon)
        self.lat = float(lat)
        self.spn = float(spn)
        self.theme = "light"  # по умолчанию светлая тема

        self.setWindowTitle("Map")
        self.setFixedSize(650, 500)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Карта
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        self.theme_button = QPushButton("Переключить тему")
        self.theme_button.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_button)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.load_map()

    def build_url(self):
        return (
            f"{SERVER}ll={self.lon},{self.lat}"
            f"&spn={self.spn},{self.spn}"
            f"&l=map"
            f"&theme={self.theme}"
            f"&apikey={API_KEY}"
        )

    def load_map(self):
        response = requests.get(self.build_url())
        if not response.ok:
            print("Ошибка запроса:", response.status_code)
            return
        pixmap = QPixmap()
        pixmap.loadFromData(response.content)
        self.label.setPixmap(pixmap)

    def toggle_theme(self):
        if self.theme == "light":
            self.theme = "dark"
        else:
            self.theme = "light"
        self.load_map()

    def keyPressEvent(self, event):
        step = self.spn / 2
        if event.key() == Qt.Key.Key_PageUp:
            self.spn = max(self.spn / ZOOM_STEP, MIN_SPN)
        elif event.key() == Qt.Key.Key_PageDown:
            self.spn = min(self.spn * ZOOM_STEP, MAX_SPN)
        elif event.key() == Qt.Key.Key_Up:
            self.lat = min(self.lat + step, 85)
        elif event.key() == Qt.Key.Key_Down:
            self.lat = max(self.lat - step, -85)
        elif event.key() == Qt.Key.Key_Right:
            self.lon = min(self.lon + step, 180)
        elif event.key() == Qt.Key.Key_Left:
            self.lon = max(self.lon - step, -180)
        else:
            return
        self.load_map()


def main():
    if len(sys.argv) != 4:
        print("Использование:")
        print("python main.py <lon> <lat> <spn>")
        sys.exit(1)

    lon = sys.argv[1]
    lat = sys.argv[2]
    spn = float(sys.argv[3])

    app = QApplication(sys.argv)
    window = MapWindow(lon, lat, spn)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
