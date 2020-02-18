import sys
from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QMessageBox
import os
import requests
from PyQt5.QtGui import QPixmap

params = {'x': 0.0, 'y': 0.0, 'zoom': 0, 'type': 'map', 'pt': ''}


class MyWidget(QMainWindow):
    def get_coords(self, target):
        response = requests.get(f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&"
                                f"geocode={target}, 1&format=json")
        response = response.json()
        try:
            self.adressLine.setText(response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                                    ["metaDataProperty"]["GeocoderMetaData"]['text'])
            return response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]['Point']['pos']
        except IndexError:
            return 'error error'

    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.x_line.editingFinished.connect(self.update)
        self.y_line.editingFinished.connect(self.update)
        self.zoomSlider.valueChanged.connect(self.update)
        self.but_map.toggled.connect(self.update)
        self.but_sat.toggled.connect(self.update)
        self.searchButton.clicked.connect(self.search_object)
        self.resetButton.clicked.connect(self.reset_search)
        self.map_file = None
        self.update()

    def get_image(self):
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={params['x']},{params['y']}&z={params['zoom']}" \
                      f"&l={params['type']}&" \
                      f"size=600,450&api_key = 40d1649f-0493-4b70-98ba-98533de7710b{params['pt']}"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        # Запишем полученное изображение в файл.
        if params['type'] != 'sat':
            self.map_file = "map.png"
        else:
            self.map_file = "map.jpg"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def update(self):
        params['x'] = float(self.x_line.text())
        params['y'] = float(self.y_line.text())
        params['zoom'] = int(self.zoomSlider.value())
        if self.but_map.isChecked():
            params['type'] = 'map'
        elif self.but_sat.isChecked():
            params['type'] = 'sat'
        else:
            params['type'] = 'skl'
        print(params)
        self.get_image()
        print(self.map_file)
        self.pixmap = QPixmap(self.map_file)
        self.label_map.setPixmap(self.pixmap)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_PageUp:
            if params['zoom'] < 17:
                params['zoom'] += 1
        if e.key() == Qt.Key_PageDown:
            if params['zoom'] > 0:
                params['zoom'] -= 1
        self.zoomSlider.setValue(params['zoom'])

    def search_object(self):
        x, y = list(self.get_coords(self.searchLine.text()).split())
        if x == 'error':
            msg = QMessageBox()
            msg.setWindowTitle('Ошибка')
            msg.setText('Объект не найден')
            ma = msg.exec()
        else:
            self.x_line.setText(x)
            self.y_line.setText(y)
            params['pt'] = f'&pt={x},{y},comma'
            self.update()

    def reset_search(self):
        params['pt'] = ''
        self.update()
        self.adressLine.setText('')
        self.searchLine.setText('')


app = QApplication(sys.argv)
ex = MyWidget()
ex.show()
sys.exit(app.exec_())