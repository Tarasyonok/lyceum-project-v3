import sqlite3
import os
import sys

from itertools import chain
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class createReminder(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        uic.loadUi('reminder.ui', self)
        self.parent = parent
        self.pushButton_2.clicked.connect(self.open_add)

    def open_add(self):
        self.opa = QMainWindow()
        uic.loadUi('alarm.ui', self.opa)
        self.opa.show()
