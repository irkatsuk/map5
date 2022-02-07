from PIL import Image
import sys
import requests
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from io import BytesIO
from PyQt5.QtCore import Qt


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(400, 400, 300, 300)
        uic.loadUi('ui/map5.ui', self)
        self.start_button.clicked.connect(self.start)
        self.scale = 17
        self.longitude = 0.0
        self.lattitude = 0.0
        self.sat = self.sat_radioButton.setChecked(True)
        self.search_pushButton.clicked.connect(self.search)

    def search(self):
        if len(self.scale_LineEdit.text()) != 0:
            self.scale = int(self.scale_LineEdit.text())
        sat = self.sat_radioButton.isChecked()
        map = self.map_radioButton.isChecked()
        hibrid = self.hibrid_radioButton.isChecked()
        st = ''
        if sat:
            st = 'sat'
        elif map:
            st = 'map'
        else:
            st = 'skl'
        if len(self.object_lineEdit.text()) == 0:
            return
        obj = self.object_lineEdit.text()
        geocoder_request = f"https://geocode-maps.yandex.ru/1.x/?" \
                           f"apikey=40d1649f-0493-4b70-98ba-98533de7710b&" \
                           f"geocode={obj}&format=json"
        response = requests.get(geocoder_request)
        if response:
            json_response = response.json()
            collection = json_response["response"]["GeoObjectCollection"]
            toponym = collection["featureMember"][0]["GeoObject"]
            # Полный адрес топонима:
            toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"][
                "text"]
            # Координаты центра топонима:
            toponym_coodrinates = toponym["Point"]["pos"]
            long = float(toponym_coodrinates.split()[0])
            latt = float(toponym_coodrinates.split()[1])
        self.paint(self.scale, long, latt, st)

    def loadPixmap(self, fname):
        self.pixmap = QPixmap(fname)
        self.im = Image.open(fname)
        self.pixels = self.im.load()  # список с пикселями
        self.x, self.y = self.im.size
        self.label_map.resize(self.x, self.y)
        # Отображаем содержимое QPixmap в объекте QLabel
        self.label_map.setPixmap(self.pixmap)
        self.label_map.repaint()

    def start(self):
        sat = self.sat_radioButton.isChecked()
        map = self.map_radioButton.isChecked()
        hibrid = self.hibrid_radioButton.isChecked()
        st = ''
        if sat:
            st = 'sat'
        elif map:
            st = 'map'
        else:
            st = 'skl'
        if len(self.scale_LineEdit.text()) == 0:
            return
        self.scale = int(self.scale_LineEdit.text())
        if len(self.lattitude_LineEdit.text()) == 0 \
                or len(self.longitude_LineEdit.text()) == 0:
            return
        self.lattitude = float(self.lattitude_LineEdit.text())
        self.longitude = float(self.longitude_LineEdit.text())
        self.paint(self.scale, self.longitude, self.lattitude, st)

    def paint(self, scale, longitude, lattitude, st):
        map_params = {
            "ll": ",".join([str(longitude), str(lattitude)]),
            "l": st,
            "z": str(scale),
            "pt": f"{str(longitude)},{str(lattitude)},pmrdm1"
        }
        map_api_server = "http://static-maps.yandex.ru/1.x/"
        response = requests.get(map_api_server, params=map_params)
        Image.open(BytesIO(
            response.content)).save("image.png")
        self.loadPixmap('image.png')

    def keyPressEvent(self, eventQKeyEvent):
        key = eventQKeyEvent.key()
        if key == Qt.Key_PageDown:
            if self.scale + 1 < 17:
                self.scale += 1
                self.start(self.scale)
        elif key == Qt.Key_PageUp:
            if self.scale - 1 > 0:
                self.scale -= 1
                self.start(self.scale)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
