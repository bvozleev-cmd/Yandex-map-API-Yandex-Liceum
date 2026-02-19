import sys
import requests
from PyQt6.QtWidgets import (
    QApplication, QLabel, QMainWindow,
    QPushButton, QWidget, QVBoxLayout,
    QLineEdit, QHBoxLayout
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

API_KEY = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"
GEOCODER_API_KEY = "8013b162-6b42-4997-9691-77b7074026e0"
STATIC_SERVER = "https://static-maps.yandex.ru/v1?"
GEOCODER_SERVER = "https://geocode-maps.yandex.ru/1.x/"
MIN_SPN = 0.0005
MAX_SPN = 50
ZOOM_STEP = 2


class MapWindow(QMainWindow):
    def __init__(self, lon, lat, spn):
        super().__init__()
        self.lon = float(lon)
        self.lat = float(lat)
        self.spn = float(spn)
        self.theme = "light"
        self.markers = []
        self.setWindowTitle("Map")
        self.setFixedSize(650, 600)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите адрес или объект...")
        self.search_input.returnPressed.connect(self.search_object)
        self.search_button = QPushButton("Искать")
        self.search_button.clicked.connect(self.search_object)
        self.reset_button = QPushButton("Сброс поискового результата")
        self.reset_button.clicked.connect(self.reset_last_marker)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.reset_button)
        main_layout.addLayout(search_layout)
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.label)
        self.theme_button = QPushButton("Переключить тему")
        self.theme_button.clicked.connect(self.toggle_theme)
        main_layout.addWidget(self.theme_button)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.load_map()

    def build_map_url(self):
        url = (
            f"{STATIC_SERVER}ll={self.lon},{self.lat}"
            f"&spn={self.spn},{self.spn}"
            f"&l=map"
            f"&theme={self.theme}"
            f"&apikey={API_KEY}"
        )
        if self.markers:
            pts = "~".join([f"{m},pm2rdm" for m in self.markers])
            url += f"&pt={pts}"
        return url

    def load_map(self):
        response = requests.get(self.build_map_url())
        if not response.ok:
            print("Ошибка карты:", response.status_code)
            print(response.text)
            return
        pixmap = QPixmap()
        pixmap.loadFromData(response.content)
        self.label.setPixmap(pixmap)

    def search_object(self):
        query = self.search_input.text()
        if not query:
            return
        params = {
            "apikey": GEOCODER_API_KEY,
            "geocode": query,
            "format": "json",
            "lang": "ru_RU"
        }
        response = requests.get(GEOCODER_SERVER, params=params)
        if response.status_code != 200:
            print("Ошибка геокодера:", response.status_code)
            print(response.text)
            return
        data = response.json()
        try:
            pos = data["response"]["GeoObjectCollection"] \
                ["featureMember"][0]["GeoObject"]["Point"]["pos"]
            lon, lat = pos.split()
            self.lon = float(lon)
            self.lat = float(lat)
            self.markers.append(f"{lon},{lat}")
            self.load_map()
        except (IndexError, KeyError):
            print("Объект не найден")

    def reset_last_marker(self):
        if self.markers:
            self.markers.pop()
            self.load_map()

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
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
