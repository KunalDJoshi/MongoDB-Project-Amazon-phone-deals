from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class FieldWidget(QWidget):

    def __init__(self, d, name, db):
        super(FieldWidget, self).__init__()

        self.name = name
        self.is_on = False
        self.db = db
        self.vbox = QVBoxLayout()
        info = d
        self.id = info["_id"]
        self.static_textbox1 = QLabel(self)
        self.static_textbox1.setText("Product name: " + info["Product_name"])

        self.static_textbox2 = QLabel(self)
        self.static_textbox2.setText("Company: " + info["by_info"])

        self.static_textbox3 = QLabel(self)
        url = '''<a href='{}'>Product Link</a>'''.format(info["Product_url"])
        self.static_textbox3.setOpenExternalLinks(True)
        self.static_textbox3.setText(url)

        self.static_textbox4 = QLabel(self)
        self.static_textbox4.setText("City: " + info["city"])

        self.vbox.addWidget(self.static_textbox1)
        self.vbox.addWidget(self.static_textbox2)
        self.vbox.addWidget(self.static_textbox3)
        self.vbox.addWidget(self.static_textbox4)

        # image
        if info["img"] is not None:
            self.image_frame = QLabel(self)
            cv_img = info["img"]
            # image = QImage(cv_img.data, cv_img.shape[1], cv_img.shape[0], QImage.Format_RGB888).rgbSwapped()
            image = QImage(cv_img.data, cv_img.shape[1], cv_img.shape[0], cv_img.strides[0], QImage.Format_RGB888).rgbSwapped()
            self.image_frame.setPixmap(QPixmap.fromImage(image).scaled(cv_img.shape[0]/2, cv_img.shape[1]/2, Qt.KeepAspectRatio))
            self.vbox.addWidget(self.image_frame)

        self.static_comment_box = QLabel(self)
        self.comment = ''
        if "comment" in info.keys():
            self.comment = info["comment"]
            self.static_comment_box.setText("Comment: " + self.comment)
        else:
            self.static_comment_box.setText("Comment: " + self.comment)
        self.vbox.addWidget(self.static_comment_box)

        self.comment_box = QLineEdit(self)
        self.comment_button = QPushButton('Add comment to db', self)
        self.comment_button.clicked.connect(self.add_comment)
        self.vbox.addWidget(self.comment_box)
        self.vbox.addWidget(self.comment_button)

        self.setLayout(self.vbox)
        self.setVisible(False)

    def show(self):
        # for w in [self, self.lbl]:
        for w in [self]:
            w.setVisible(True)

    def hide(self):
        # for w in [self, self.lbl]:
        for w in [self]:
            w.setVisible(False)

    def add_comment(self):

        comment = self.comment_box.text()
        print("Entered comment is: {}".format(comment))
        self.static_comment_box.repaint()

        if self.comment == '':
            self.comment = comment
        else:
            self.comment += ' | ' + comment
        self.static_comment_box.setText("Comment: " + self.comment)
        self.db.update({"_id": self.id}, {"$set": {"comment": self.comment}})


