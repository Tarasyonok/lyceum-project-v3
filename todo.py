import sqlite3

from itertools import chain
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from createTask import createTask
from editTask import editTask
from categoriesSettings import categoriesSettings
from createReminder import createReminder


class todo(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('todo.ui', self)
        self.tasksList.setIconSize(QSize(20, 20))
        self.tasksList.setFont(QFont("Times", 12, QFont.Black))

        self.addBtn.clicked.connect(self.add_task)

        # self.tasksList.itemClicked.connect(self.update_box)
        self.tasksList.itemDoubleClicked.connect(self.show_right_part)

        self.today.clicked.connect(self.load_today)
        self.tomorrow.clicked.connect(self.load_tomorrow)
        self.daily.clicked.connect(self.load_daily)

        self.categoriesSettingsBtn.clicked.connect(self.open_categories_settings)
        self.reminderBtn.clicked.connect(self.create_reminder)

        self.deleteBtn.clicked.connect(self.delete_task)
        self.editBtn.clicked.connect(self.show_edit_task)

        self.hide_right_part()

        self.curr_plan = ''

        self.load_today()

    def load_tasks(self):
        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()

        result1 = cur.execute(f"""
        SELECT {self.curr_plan}.title, IFNULL(categories.color, '255 255 255')
        FROM {self.curr_plan}
        LEFT JOIN categories
        ON {self.curr_plan}.category = categories.id
        """).fetchall()

        if self.curr_plan == 'tomorrow':
            result2 = cur.execute(f"""
            SELECT Daily.title, IFNULL(categories.color, '255 255 255')
            FROM Daily
            LEFT JOIN categories
            ON Daily.category = categories.id
            """).fetchall()

            result3 = cur.execute(f"""
            SELECT Today.title, IFNULL(categories.color, '255 255 255')
            FROM Today
            LEFT JOIN categories
            ON Today.category = categories.id
            WHERE Today.isDone = 0
            """).fetchall()
            result = chain(result1, result2, result3)
        else:
            result = result1

        self.tasksList.clear()
        for elem in result:
            # print(elem)
            item = QListWidgetItem()
            if elem[1]:
                c1, c2, c3 = map(int, elem[1].split())
                item.setBackground(QColor(c1, c2, c3))
                # print(c1, c2, c3)
            # if self.curr_plan == 'today':
            #     if elem[1] == 0:
            #         icon = QIcon('checkboxOff.png')
            #     else:
            #         icon = QIcon('checkboxOn.png')
            #     item.setIcon(icon)
            item.setText(elem[0])
            self.tasksList.addItem(item)
        con.close()

    def load_today(self):
        if self.curr_plan != 'today':
            self.hide_right_part()
        self.curr_plan = 'today'
        self.planLabel.setText("План на сегодня")
        self.load_tasks()

    def load_tomorrow(self):
        if self.curr_plan != 'tomorrow':
            self.hide_right_part()
        self.curr_plan = 'tomorrow'
        self.planLabel.setText("План на завтра")
        self.load_tasks()

    def load_daily(self):
        if self.curr_plan != 'daily':
            self.hide_right_part()
        self.curr_plan = 'daily'
        self.planLabel.setText("Ежедневные дела")
        self.load_tasks()

    def update_box(self, item):
        if self.curr_plan != 'today':
            return
        text = item.text()

        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()
        result = cur.execute("""SELECT isDone FROM Today WHERE text = ?""", (text,)).fetchone()
        if result[0] == 1:
            icon = QIcon('checkboxOff.png')
            item.setIcon(icon)
            cur.execute("""UPDATE Today SET isDone = 0 WHERE text = ?""", (text,))
            try:
                cur.execute("""UPDATE Today SET isDone = 0 WHERE text = ?""", (text,))
            except:
                pass
        else:
            icon = QIcon('checkboxOn.png')
            item.setIcon(icon)
            cur.execute("""UPDATE Today SET isDone = 1 WHERE text = ?""", (text,))
        con.commit()
        con.close()

    def add_task(self):
        self.create_edit = createTask(self, self.curr_plan)
        self.create_edit.show()


    def hide_right_part(self):
        self.titleLabel.hide()
        self.title.hide()

        self.categoryLabel.hide()
        self.category.hide()

        self.repeatLabel.hide()
        self.repeat.hide()

        self.descriptionLabel.hide()
        self.description.hide()

        self.deleteBtn.hide()
        self.markAsDoneBtn.hide()
        self.editBtn.hide()

    def show_right_part(self, item):
        index = self.tasksList.indexFromItem(item).row()

        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()

        if self.curr_plan == 'today':
            info = cur.execute(f"""SELECT * FROM Today""").fetchall()
        elif self.curr_plan == 'tomorrow':
            info1 = cur.execute(f"""SELECT * FROM Tomorrow""").fetchall()
            info2 = cur.execute(f"""SELECT * FROM Daily""").fetchall()
            info3 = cur.execute(f"""SELECT * FROM Today WHERE isDone = 0""").fetchall()
            info = list((chain(info1, info2, info3)))
        elif self.curr_plan == 'daily':
            info = cur.execute(f"""SELECT * FROM Daily""").fetchall()





        result = info[index]

        print(result)

        if result[3]:
            cat = cur.execute(f"""
            SELECT IFNULL(title, 'Без категории') FROM Categories
            WHERE id = {result[3]}
            """).fetchone()[0]
        else:
            cat = 'Без категории'

        print(cat)

        # print(index)

        # result = cur.execute(f"""
        # SELECT {self.curr_plan}.title, IFNULL(categories.title, 'Без категории'), {self.curr_plan}.description
        # FROM {self.curr_plan}
        # LEFT JOIN categories
        # ON {self.curr_plan}.category = categories.id
        # WHERE {self.curr_plan}.id = {curr_id}
        # """).fetchone()

        # if self.curr_plan == 'daily':
        #     repeat = cur.execute(f"""
        #     SELECT repeat FROM Daily
        #     WHERE id = {curr_id}
        #     """).fetchone()

        # res = cur.execute("""
        # SELECT films.id, films.title, films.year, IFNULL(genres.title, films.genre), films.duration FROM films
        # LEFT JOIN genres
        # ON films.genre = genres.id
        # ORDER BY films.id DESC
        # """).fetchall()


        self.task_id = result[0]

        self.titleLabel.show()
        self.title.clear()
        self.title.append(result[1])
        self.title.show()

        self.categoryLabel.show()
        self.category.clear()
        self.category.append(cat)
        self.category.show()

        if self.curr_plan == 'daily':
            self.repeatLabel.show()
            self.repeat.clear()
            self.repeat.append(result[-1])
            self.repeat.show()

        self.descriptionLabel.show()
        self.description.clear()
        self.description.append(result[2])
        self.description.show()

        if self.curr_plan != 'tomorrow':
            self.deleteBtn.show()
            self.markAsDoneBtn.show()
            self.editBtn.show()

    def open_categories_settings(self):
        self.categories_settings = categoriesSettings(self)
        self.categories_settings.show()

    def delete_task(self):
        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()

        # x = QMessageBox.question(self, "Внимание",
        #                          f'Действительно удалить категорию "{title}"?\n (Все дела с этой категорией станут без категории)')
        # if x > 50000:
        #     return

        cur.execute(f"""
        DELETE FROM {self.curr_plan}
        WHERE id = {self.task_id}
        """)

        con.commit()

        self.load_tasks()

        self.hide_right_part()

        self.statusBar().showMessage("Дело успешно удалено")


    def show_edit_task(self):
        self.edit_task = editTask(self, self.curr_plan, self.task_id)
        self.edit_task.show()

    def create_reminder(self):
        self.reminder = createReminder(self)
        self.reminder.show()

