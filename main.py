import sys
import requests
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QThread, pyqtSignal

API_KEY = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"
SERVER = "https://static-maps.yandex.ru/v1?"
MIN_SPN = 0.0005
MAX_SPN = 50
ZOOM_STEP = 2
MOVE_FACTOR = 0.5


class MapLoader(QThread):
    finished = pyqtSignal(bytes)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            response = requests.get(self.url)
            if response.ok:
                self.finished.emit(response.content)
        except Exception as e:
            print("Ошибка загрузки карты:", e)


class MapWindow(QMainWindow):
    def __init__(self, lon, lat, spn):
        super().__init__()
        self.lon = float(lon)
        self.lat = float(lat)
        self.spn = float(spn)
        self.setWindowTitle("Map")
        self.setFixedSize(650, 450)
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.label)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.load_map_async()

    def build_url(self):
        return (
            f"{SERVER}ll={self.lon},{self.lat}"
            f"&spn={self.spn},{self.spn}"
            f"&l=map&apikey={API_KEY}"
        )

    def load_map_async(self):
        self.loader = MapLoader(self.build_url())
        self.loader.finished.connect(self.update_map)
        self.loader.start()

    def update_map(self, data):
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        self.label.setPixmap(pixmap)

    def keyPressEvent(self, event):
        step = self.spn * MOVE_FACTOR
        if event.key() == Qt.Key.Key_PageUp:
            self.spn /= ZOOM_STEP
            if self.spn < MIN_SPN:
                self.spn = MIN_SPN
        elif event.key() == Qt.Key.Key_PageDown:
            self.spn *= ZOOM_STEP
            if self.spn > MAX_SPN:
                self.spn = MAX_SPN
        elif event.key() == Qt.Key.Key_Up:
            self.lat += step
            if self.lat > 85:
                self.lat = 85
        elif event.key() == Qt.Key.Key_Down:
            self.lat -= step
            if self.lat < -85:
                self.lat = -85
        elif event.key() == Qt.Key.Key_Right:
            self.lon += step
            if self.lon > 180:
                self.lon -= 360
        elif event.key() == Qt.Key.Key_Left:
            self.lon -= step
            if self.lon < -180:
                self.lon += 360
        else:
            return
        self.load_map_async()


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
