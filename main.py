import sys
import os
import requests
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

API_KEY = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
SERVER = 'https://static-maps.yandex.ru/v1?'
MAP_FILE = 'map.png'


class MapWindow(QWidget):
    def __init__(self, lon, lat, spn_x, spn_y):
        super().__init__()
        self.setWindowTitle("MAP")
        self.setFixedSize(650, 450)
        self.lon = lon
        self.lat = lat
        self.spn_x = spn_x
        self.spn_y = spn_y
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.load_map()

    def load_map(self):
        params = (
            f"ll={self.lon},{self.lat}"
            f"&spn={self.spn_x},{self.spn_y}"
            f"&l=map"
            f"&apikey={API_KEY}"
        )
        response = requests.get(SERVER + params)
        if not response:
            print("Ошибка запроса:", response.status_code)
            sys.exit(1)
        with open(MAP_FILE, "wb") as f:
            f.write(response.content)
        pixmap = QPixmap(MAP_FILE)
        self.label.setPixmap(pixmap)
        self.label.resize(pixmap.size())


def main():
    if len(sys.argv) != 5:
        print("Использование:")
        print("python main.py <lon> <lat> <spn_x> <spn_y>")
        sys.exit(1)
    lon = sys.argv[1]
    lat = sys.argv[2]
    spn_x = sys.argv[3]
    spn_y = sys.argv[4]
    app = QApplication(sys.argv)
    window = MapWindow(lon, lat, spn_x, spn_y)
    window.show()
    exit_code = app.exec()
    if os.path.exists(MAP_FILE):
        os.remove(MAP_FILE)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()