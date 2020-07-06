
# from pymongo import Connection
#import pymongo
from pymongo import MongoClient
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import numpy as np
import gridfs
import codecs
import cv2
from fields import FieldWidget

conn = "mongodb+srv://muriel82:Muriel824@cluster0-kxon7.mongodb.net/test?retryWrites=true&w=majority"

db = MongoClient(conn)
curr_proj = db.get_database("mongodbproject")
curr_proj1 = db.get_database("amazonImages")
fs = gridfs.GridFS(curr_proj1)
image_dataset = curr_proj1.get_collection('Images')
cnt = 0
id2img = {}
img2id = {}
for f in image_dataset.find():
    id2img.update({str(f["_id"]) : str(f["imgSrc"])})
    img2id.update({str(f["imgSrc"]): str(f["_id"])})
all_imgs = list(fs.find())
all_imgs_dict = {}
TOTAL_LOAD_IMG_CNT = 10
image_load_cnt = 0
for img in all_imgs:
    all_imgs_dict[str(img._id)] = img
phone_dataset = curr_proj.get_collection('amazon_phone_dataset')
tot = 0
blank_info_cnt = 0
phone_data_modified = []
cities = set()
companies = set()
cities_dict = {}
companies_dict = {}
for phone_data in phone_dataset.find():
    # print(phone_data)
    tot += 1
    if phone_data["Product_name"] == '':
        blank_info_cnt += 1
    else:
        curr_city = phone_data["city"].lower()
        cities.add(curr_city)
        curr_company = phone_data["by_info"].lower()
        companies.add(curr_company)
        phone_data_modified.append(phone_data)

        phone_data["img"] = None
        if phone_data["Product_img"] != '':
            try:
                print(image_load_cnt)
                if image_load_cnt < TOTAL_LOAD_IMG_CNT:
                    curr_id = phone_data["_id"]
                    image = all_imgs_dict[id2img[str(curr_id)]]
                    base64_data = codecs.encode(image.read(), 'base64')
                    nparr = np.fromstring(codecs.decode(base64_data, 'base64'), np.uint8)
                    img = cv2.imdecode(nparr, cv2.IMREAD_ANYCOLOR)
                    phone_data["img"] = img
                    image_load_cnt += 1
                    print(phone_data["city"])
            except Exception as e:
                pass

        if curr_city not in cities_dict.keys():
            cities_dict[curr_city] = [phone_data]
        else:
            cities_dict[curr_city].append(phone_data)

        if curr_company not in companies_dict.keys():
            companies_dict[curr_company] = [phone_data]
        else:
            companies_dict[curr_company].append(phone_data)

print("Loaded database")

# create two input fields
class MyWidget(QWidget):

    def __init__(self, name):
        super(MyWidget, self).__init__()

        self.name = name
        self.is_on = False

        # self.lbl = QLabel(self.name)
        self.btn_on = QPushButton(self.name)

        self.hbox = QHBoxLayout()
        # self.hbox.addWidget(self.lbl)
        self.hbox.addWidget(self.btn_on)

        self.btn_on.clicked.connect(self.on)

        self.hbox.setAlignment(Qt.AlignLeft)
        self.setLayout(self.hbox)
        self.update_button_state()
        self.setVisible(False)

    def show(self):
        # for w in [self, self.lbl]:
        for w in [self, self.btn_on]:
            w.setVisible(True)

    def hide(self):
        # for w in [self, self.lbl]:
        for w in [self, self.btn_on]:
            w.setVisible(False)

    def off(self):
        self.is_on = False
        self.update_button_state()

    def on(self):
        self.is_on = True
        self.update_button_state()

    def update_button_state(self):
        """
        Update the appearance of the control buttons (On/Off)
        depending on the current state.
        """
        if self.is_on == True:
            self.btn_on.setStyleSheet("background-color: #4CAF50; color: #fff;")
            # self.btn_off.setStyleSheet("background-color: none; color: none;")
        else:
            self.btn_on.setStyleSheet("background-color: none; color: none;")
            # self.btn_off.setStyleSheet("background-color: #D32F2F; color: #fff;")


class App(QMainWindow):
    EXIT_CODE_REBOOT = -123
    def __init__(self):
        super().__init__()
        self.title = 'Amazon Phone reviews'
        # self.left = 100
        # self.top = 100
        # self.width = 600
        # self.height = 400
        # self.initUI()
        self.option = None
        self.controls = QWidget()  # Controls container widget.
        self.controlsLayout = QVBoxLayout()   # Controls container layout.

        self.cities = []
        for name in cities:
            item = MyWidget(name)
            self.controlsLayout.addWidget(item)
            self.cities.append(item)

        self.companies = []
        for company in companies:
            item = MyWidget(company)
            self.controlsLayout.addWidget(item)
            self.companies.append(item)

        self.static_textbox = QLabel(self)
        self.static_textbox.setText("Search by brand name or location")
        # self.static_textbox.setAlignment(Qt.AlignLeft)

        self.radiobutton1 = QRadioButton("Brand name")
        self.radiobutton1.setChecked(False)
        self.radiobutton1.name = "brand"
        self.radiobutton1.toggled.connect(self.onClicked)

        self.radiobutton2 = QRadioButton("Location")
        self.radiobutton2.setChecked(False)
        self.radiobutton2.name = "location"
        self.radiobutton2.toggled.connect(self.onClicked)

        # Search bar.
        self.searchbar = QLineEdit()
        self.searchbar.move(40, 40)
        self.searchbar.resize(380,40)
        self.searchbar.textChanged.connect(self.update_display)

        self.reset_button = QPushButton('Reset', self)
        self.reset_button.clicked.connect(self.on_click_reset)

        self.restart_button = QPushButton('Restart', self)
        self.restart_button.clicked.connect(self.on_click_restart)

        self.button = QPushButton('Show details', self)
        self.button.clicked.connect(self.on_click)

        spacer = QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.controlsLayout.addItem(spacer)
        self.controls.setLayout(self.controlsLayout)

        # Scroll Area Properties.
        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.controls)

        # Adding Completer.
        # self.completer = QCompleter(cities)
        # self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        # self.searchbar.setCompleter(self.completer)

        # Add the items to VBoxLayout (applied to container widget)
        # which encompasses the whole window.
        container = QWidget()
        containerLayout = QVBoxLayout()
        containerLayout.addWidget(self.static_textbox)
        containerLayout.addWidget(self.radiobutton1)
        containerLayout.addWidget(self.radiobutton2)
        containerLayout.addWidget(self.searchbar)
        containerLayout.addWidget(self.reset_button)
        containerLayout.addWidget(self.button)
        # containerLayout.addWidget(self.scroll)
        # container.setLayout(containerLayout)
        # self.setCentralWidget(container)

        ####
        container1 = QWidget()
        containerLayout1 = QHBoxLayout()

        self.controls1 = QWidget()  # Controls container widget.
        self.controlsLayout1 = QVBoxLayout()
        self.cities_dict = {}
        for name in cities_dict.keys():
            self.cities_dict[name] = []
            for each_dict in cities_dict[name]:
                item = FieldWidget(each_dict, name, phone_dataset)
                self.controlsLayout.addWidget(item)
                self.cities_dict[name].append(item)
        #
        self.companies_dict = {}
        for company in companies_dict.keys():
            self.companies_dict[company] = []
            for each_dict in companies_dict[company]:
                item = FieldWidget(each_dict, company, phone_dataset)
                self.controlsLayout.addWidget(item)
                self.companies_dict[company].append(item)

        self.scroll1 = QScrollArea()
        self.scroll1.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll1.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll1.setWidgetResizable(True)
        # self.scroll1.setWidget(self.controls1)

        containerLayout1.addWidget(self.scroll, 50)
        containerLayout1.addWidget(self.scroll1, 50)
        containerLayout.addLayout(containerLayout1)
        containerLayout.addWidget(self.restart_button)
        container.setLayout(containerLayout)
        self.setCentralWidget(container)

    # self.setGeometry(600, 100, 800, 600)
        self.setWindowTitle(self.title)
        # self.show()
        self.showMaximized()


    def update_display(self, text):
        if text == "":
            return
        if self.option == "location":
            for widget in self.cities:
                if text.lower() in widget.name.lower() and widget.name.lower().startswith(text.lower()):
                    widget.show()
                else:
                    widget.hide()

        if self.option == "brand":
            for widget in self.companies:
                if text.lower() in widget.name.lower() and widget.name.lower().startswith(text.lower()):
                    widget.show()
                else:
                    widget.hide()

    def onClicked(self):
        for c in self.cities:
            c.hide()
        for c in self.companies:
            c.hide()
        # for n in self.cities_dict.keys():
        #     print(n)
        #     self.cities_dict[n][0].show()
        #     self.cities_dict["denver"][0].show()
        #     break
        radioButton = self.sender()
        if radioButton.isChecked():
            print("option is %s" % (radioButton.name))
            self.option = radioButton.name.lower()
            # return radioButton.name

    @pyqtSlot()
    def on_click_reset(self):
        for widget in self.cities:
            widget.off()
            if widget.isVisible():
                widget.hide()
        for widget in self.companies:
            widget.off()
            if widget.isVisible():
                widget.hide()

        for k in self.cities_dict.keys():
            for widget in self.cities_dict[k]:
                if widget.isVisible():
                    widget.hide()
        for k in self.companies_dict.keys():
            for widget in self.companies_dict[k]:
                if widget.isVisible():
                    widget.hide()

        # self.radiobutton1.setDisabled(True)
        # self.radiobutton2.setDisabled(True)
        self.radiobutton1.setAutoExclusive(False)
        self.radiobutton2.setAutoExclusive(False)

        self.radiobutton1.setChecked(False)
        self.radiobutton2.setChecked(False)

        self.radiobutton1.setAutoExclusive(True)
        self.radiobutton2.setAutoExclusive(True)

    @pyqtSlot()
    def on_click_restart(self):
        qApp.exit(App.EXIT_CODE_REBOOT )

    @pyqtSlot()
    def on_click(self):
        if self.option == 'location':
            for n in self.cities_dict.keys():
                for i, selected_widgets in enumerate(self.cities):
                    if n == selected_widgets.name and selected_widgets.is_on:
                        for widget in self.cities_dict[n]:
                            widget.show()
                        self.cities[i].is_on = False
                        return
        elif self.option == 'brand':
            for n in self.companies_dict.keys():
                for i, selected_widgets in enumerate(self.companies):
                    if n == selected_widgets.name and selected_widgets.is_on:
                        for widget in self.companies_dict[n]:
                            widget.show()
                        self.companies[i].is_on = False
                        return

                        # def initUI(self):
    #     self.setWindowTitle(self.title)
    #     self.setGeometry(self.left, self.top, self.width, self.height)
    #
    #     # create text
    #     self.static_textbox = QLabel(self)
    #     self.static_textbox.setText("Search by brand name or location")
    #     # self.static_textbox.setAlignment(Qt.AlignLeft)
    #     self.static_textbox.move(20, 20)
    #     self.static_textbox.resize(380,40)
    #
    #     layout = QVBoxLayout()  # layout for the central widget
    #     widget = QWidget(self)  # central widget
    #     widget.setLayout(layout)
    #     # layout = QGridLayout()
    #     # self.setLayout(layout)
    #     self.radiobutton1 = QRadioButton("Brand name")
    #     self.radiobutton1.setChecked(False)
    #     self.radiobutton1.name = "Brand name"
    #     # radiobutton.move(100, 100)
    #     # radiobutton.setGeometry(QRect(160, 80, 40, 17))
    #     self.radiobutton1.toggled.connect(self.onClicked)
    #     layout.addWidget(self.radiobutton1, 0)
    #     # self.layout().addWidget(radiobutton, 0, 0)
    #
    #     self.radiobutton2 = QRadioButton("Location")
    #     self.radiobutton2.name = "Location"
    #     # radiobutton.move(100, 100)
    #     self.radiobutton2.setGeometry(QRect(160, 80, 40, 17))
    #     self.radiobutton2.toggled.connect(self.onClicked)
    #     layout.addWidget(self.radiobutton2, 1)
    #     # self.layout().addWidget(radiobutton, 0, 1)
    #     self.setCentralWidget(widget)
    #
    #     # Create textbox
    #     self.textbox = QLineEdit(self)
    #     self.textbox.move(20, 80)
    #     self.textbox.resize(380,40)
    #
    #     # Create a button in the window
    #     self.button = QPushButton('Predict celebrity\'s gender, age and profession', self)
    #     self.button.move(20,140)
    #     self.button.resize(380,40)
    #
    #     # connect button to function on_click
    #     self.button.clicked.connect(self.on_click)
    #     self.show()
    #
    # def onClicked(self):
    #     radioButton = self.sender()
    #     if radioButton.isChecked():
    #         print("Country is %s" % (radioButton.name))
    #         self.option = radioButton.name
    #         return radioButton.name
    #
    # @pyqtSlot()
    # def on_click(self):
    #     textboxValue = self.textbox.text()
    #
    #     text = self.radiobutton1.toggled.connect(self.onClicked)
    #     print("option is {}".format(text))
    #     # self.radiobutton1.toggled.connect(self.onClicked)
    #
    #     if self.option == "Location":
    #         location_list = [x for x in phone_data_modified if textboxValue in x["city"]]
    #         self.listwidget = QListWidget()
    #         self.listwidget.move(500,500)
    #         for l in location_list:
    #             print(l["city"])
    #             self.update()
    #             self.listwidget.insertItem(l["city"])
    #             self.update()
    #
    #         layout = QVBoxLayout()  # layout for the central widget
    #         widget = QWidget(self)  # central widget
    #         widget.setLayout(layout)
    #         layout.addWidget(self.listwidget)
    #
    #
    #     gender, age, occupation = ["male", 1960, "sports"]
    #
    #     # print(age, gender, occupation)
    #     print_msg = "Age: {}  | Gender: {} | Profession: {}".format(age, gender, occupation)
    #     QMessageBox.question(self, 'Predicted traits', print_msg, QMessageBox.Ok, QMessageBox.Ok)
    #     self.textbox.setText("")

if __name__ == '__main__':
    curr_exit_code = App.EXIT_CODE_REBOOT
    while curr_exit_code == App.EXIT_CODE_REBOOT:
        app = QApplication(sys.argv)
        ex = App()
        # sys.exit(app.exec_())
        curr_exit_code = app.exec_()
        app = None