import sys
import requests
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
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
        self.lon = lon
        self.lat = lat
        self.spn = spn
        self.setWindowTitle("Map")
        self.setFixedSize(650, 450)
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.label)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.load_map()

    def load_map(self):
        params = (
            f"ll={self.lon},{self.lat}"
            f"&spn={self.spn},{self.spn}"
            f"&l=map"
            f"&apikey={API_KEY}"
        )
        response = requests.get(SERVER + params)
        if not response.ok:
            print("Ошибка запроса:", response.status_code)
            sys.exit(1)
        pixmap = QPixmap()
        pixmap.loadFromData(response.content)
        self.label.setPixmap(pixmap)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_PageUp:
            self.spn /= ZOOM_STEP
            if self.spn < MIN_SPN:
                self.spn = MIN_SPN
            self.load_map()
        elif event.key() == Qt.Key.Key_PageDown:
            self.spn *= ZOOM_STEP
            if self.spn > MAX_SPN:
                self.spn = MAX_SPN
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
