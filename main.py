import sys
import requests
from PyQt6.QtWidgets import (
    QApplication, QLabel, QMainWindow,
    QPushButton, QWidget, QVBoxLayout,
    QLineEdit, QHBoxLayout
)
from PyQt6.QtGui import QPixmap, QMouseEvent
from PyQt6.QtCore import Qt

API_KEY = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"
GEOCODER_API_KEY = "8013b162-6b42-4997-9691-77b7074026e0"
STATIC_SERVER = "https://static-maps.yandex.ru/v1?"
GEOCODER_SERVER = "https://geocode-maps.yandex.ru/1.x/"
MIN_SPN = 0.0005
MAX_SPN = 50
ZOOM_STEP = 2
MAP_WIDTH = 650
MAP_HEIGHT = 500


class MapLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.click_callback = None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.click_callback:
            x = event.position().x()
            y = event.position().y()
            self.click_callback(x, y)


class MapWindow(QMainWindow):
    def __init__(self, lon, lat, spn):
        super().__init__()
        self.lon = float(lon)
        self.lat = float(lat)
        self.spn = float(spn)
        self.theme = "light"
        self.markers = []
        self.show_postcode = True
        self.current_address = ""
        self.current_postcode = ""
        self.setWindowTitle("Map")
        self.setFixedSize(650, 700)
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
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        main_layout.addLayout(search_layout)
        self.reset_button = QPushButton("Сброс поискового результата")
        self.reset_button.clicked.connect(self.reset_last_marker)
        main_layout.addWidget(self.reset_button)
        self.postcode_button = QPushButton("Включить/выключить индекс")
        self.postcode_button.clicked.connect(self.toggle_postcode)
        main_layout.addWidget(self.postcode_button)
        self.address_label = QLabel("Адрес будет показан здесь")
        self.address_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.address_label.setWordWrap(True)
        self.address_label.setFixedHeight(40)
        main_layout.addWidget(self.address_label)
        self.label = MapLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFixedSize(MAP_WIDTH, MAP_HEIGHT)
        self.label.click_callback = self.click_on_map
        main_layout.addWidget(self.label)
        self.theme_button = QPushButton("Переключить тему")
        self.theme_button.clicked.connect(self.toggle_theme)
        main_layout.addWidget(self.theme_button)
        zoom_layout = QHBoxLayout()
        self.zoom_in_button = QPushButton("+")
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_out_button = QPushButton("-")
        self.zoom_out_button.clicked.connect(self.zoom_out)
        zoom_layout.addWidget(self.zoom_in_button)
        zoom_layout.addWidget(self.zoom_out_button)
        main_layout.addLayout(zoom_layout)
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

    def update_address_label(self):
        if self.show_postcode and self.current_postcode:
            self.address_label.setText(f"{self.current_address}, {self.current_postcode}")
        else:
            self.address_label.setText(self.current_address)

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
            return
        data = response.json()
        try:
            geo_obj = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            pos = geo_obj["Point"]["pos"]
            lon, lat = pos.split()
            self.lon = float(lon)
            self.lat = float(lat)
            self.markers.append(f"{lon},{lat}")
            meta = geo_obj["metaDataProperty"]["GeocoderMetaData"]
            self.current_address = meta["text"]
            self.current_postcode = meta.get("Address", {}).get("postal_code", "")
            self.update_address_label()
            self.load_map()
        except (IndexError, KeyError):
            self.address_label.setText("Объект не найден")
            print("Объект не найден")

    def click_on_map(self, x, y):
        lon = self.lon + (x - MAP_WIDTH / 2) * self.spn / MAP_WIDTH
        lat = self.lat - (y - MAP_HEIGHT / 2) * self.spn / MAP_HEIGHT
        query = f"{lon},{lat}"
        params = {
            "apikey": GEOCODER_API_KEY,
            "geocode": query,
            "format": "json",
            "lang": "ru_RU"
        }
        response = requests.get(GEOCODER_SERVER, params=params)
        if response.status_code != 200:
            print("Ошибка геокодера:", response.status_code)
            return
        data = response.json()
        try:
            geo_obj = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            pos = geo_obj["Point"]["pos"]
            lon, lat = pos.split()
            self.markers.append(f"{lon},{lat}")  # метка добавляется
            meta = geo_obj["metaDataProperty"]["GeocoderMetaData"]
            self.current_address = meta["text"]
            self.current_postcode = meta.get("Address", {}).get("postal_code", "")
            self.update_address_label()
            self.load_map()
        except (IndexError, KeyError):
            self.address_label.setText("Объект не найден")
            print("Объект не найден")

    def reset_last_marker(self):
        if self.markers:
            self.markers.pop()
        self.current_address = ""
        self.current_postcode = ""
        self.address_label.setText("Адрес будет показан здесь")
        self.load_map()

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.load_map()

    def toggle_postcode(self):
        self.show_postcode = not self.show_postcode
        self.update_address_label()

    def zoom_in(self):
        self.spn = max(self.spn / ZOOM_STEP, MIN_SPN)
        self.load_map()

    def zoom_out(self):
        self.spn = min(self.spn * ZOOM_STEP, MAX_SPN)
        self.load_map()

    def keyPressEvent(self, event):
        step = self.spn / 2
        if event.key() == Qt.Key.Key_PageUp:
            self.zoom_in()
        elif event.key() == Qt.Key.Key_PageDown:
            self.zoom_out()
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
