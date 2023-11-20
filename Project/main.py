import os
import random
import re
import sys

"""
для того чтобы всё было по pep-8 использовал онлайн-форматировщик
он расположил импорты библиотек вот таким забавным образом, в столбик
"""
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QDialog,
    QMessageBox,
    QAction,
    QToolBar,
    QWidget,
    QCheckBox,
    qApp,
    QComboBox,
    QFileDialog,
    QTextBrowser,
)
from PyQt5.QtGui import QIcon, QPixmap
import sqlite3
from PyQt5.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QFormLayout,
    QDialogButtonBox,
)
from PyQt5.QtCore import QTimer, QUrl, Qt
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent


class Contact:
    def __init__(self, name, email, phone):
        self.name = name
        self.email = email
        self.phone = phone


"""
ПОНЯТИЯ не имею что делает функция ниже, но она помогла
собрать exeшник)
"""


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class AboutDialog(QDialog):
    def __init__(self, parent=None, app_name="Справочник контактов"):
        super().__init__(parent)
        self.setWindowTitle(f"О приложении {app_name}")
        self.setWindowIcon(QIcon(resource_path("app-icon.png")))
        self.layout = QVBoxLayout()
        logo_label = QLabel()
        logo_pixmap = QPixmap(resource_path("my-logo.png"))
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(logo_label)
        """
        здесь были использованы очень интересный для меня
        QTextBrowser
        мы вроде его не изучали, и не сталкивались
        сам о нём вычитал и запихнул сюда... не то чтобы сюда что-то другое
        не подходило, просто внесло бы разнообразие в виджеты)
        """
        about_text = QTextBrowser()
        about_text.setOpenExternalLinks(True)
        about_text.setHtml(
            f"""
            <h1>{app_name}</h1>
            <p>Это справочник контактов, который поможет вам управлять вашими контактами легко и удобно.</p>
            <p>С его помощью вы можете добавлять, редактировать и удалять контакты, а также выполнять поиск по вашим записям.</p>
            <p>Свяжитесь с нами для поддержки и предложений: <a href="mailto:itk.dik@gmail.com">itk.dik@gmail.com</a></p>
        """
        )
        #да никак тут короче не сделать и просто перенос на другую строку не выполнить. пусть уже будет так
        self.layout.addWidget(about_text)
        self.setLayout(self.layout)


class AddContactDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить контакт")
        self.setWindowIcon(QIcon(resource_path("add-contact.ico")))
        self.name_label = QLabel("Имя:")
        self.name_lineEdit = QLineEdit()
        self.email_label = QLabel("Почта:")
        self.email_lineEdit = QLineEdit()
        self.phone_label = QLabel("Телефон:")
        self.phone_lineEdit = QLineEdit()
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout = QFormLayout()
        layout.addRow(self.name_label, self.name_lineEdit)
        layout.addRow(self.email_label, self.email_lineEdit)
        layout.addRow(self.phone_label, self.phone_lineEdit)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def get_contact(self):
        name = self.name_lineEdit.text().strip()
        email = self.email_lineEdit.text().strip()
        phone = self.phone_lineEdit.text().strip()

        if name and email and phone:
            return Contact(name, email, phone)
        else:
            return None

    """
    регулярка вроде верная, но она не работает...
    раньше ещё ниже была функция с регуляркой которая проверяет номер, но
    она проверяла соответствие только российский формат номеров,
    поэтому она скорее бы мешала, чем помогала хоть чем-то
    """

    def is_valid_email(self, email):
        return re.match(r"^[\w\.-]+@[\w\.-]+$", email)

    def show_error_message(self, message):
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle("Ошибка")
        error_dialog.setText(message)
        error_dialog.exec()


class EditContactDialog(QDialog):
    def __init__(self, parent, name, email, phone):
        super().__init__(parent)
        self.setWindowTitle("Редактировать контакт")
        self.setWindowIcon(QIcon(resource_path("edit-contact.ico")))
        self.name_label = QLabel("Имя:")
        self.name_lineEdit = QLineEdit()
        self.name_lineEdit.setText(name)
        self.email_label = QLabel("Почта:")
        self.email_lineEdit = QLineEdit(email)
        self.phone_label = QLabel("Телефон:")
        self.phone_lineEdit = QLineEdit(phone)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout = QFormLayout()
        layout.addRow(self.name_label, self.name_lineEdit)
        layout.addRow(self.email_label, self.email_lineEdit)
        layout.addRow(self.phone_label, self.phone_lineEdit)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def get_contact(self):
        name = self.name_lineEdit.text().strip()
        email = self.email_lineEdit.text().strip()
        phone = self.phone_lineEdit.text().strip()

        if name and email and phone:
            return Contact(name, email, phone)
        else:
            return None


class ContactsMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        """
        ТУТ и ниже ПОЛНЫЙ ХАОС!!!
        дезигнер для слабых, мужики добавляют в самом коде
        """
        self.setWindowTitle("Книга контактов")
        self.setWindowIcon(QIcon(resource_path("contacts.ico")))
        self.setGeometry(600, 300, 600, 600)
        self.table = QTableWidget()
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)
        self.music_button = QPushButton("Включить музыку", self)
        self.music_button.clicked.connect(self.toggle_music)
        self.toolbar.addWidget(self.music_button)
        self.player = QMediaPlayer()
        self.playlist = QMediaPlaylist()
        self.player.setPlaylist(self.playlist)
        """
        Не особо оригинальная реализация проигрывания музыки... Но лучше так, чем никак
        """
        self.music_files = [resource_path("music1.mp3"), resource_path("music2.mp3"), resource_path("music3.mp3"), resource_path("music4.mp3")]
        random_music_file = random.choice(self.music_files)
        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(random_music_file)))
        self.player.play()
        self.music_timer = QTimer(self)
        self.music_timer.timeout.connect(self.check_music_state)
        self.music_timer.start(1000)
        self.music_timer = QTimer(self)
        self.music_timer.timeout.connect(self.check_music_state)
        self.music_timer.start(1000)
        self.add_contact_action = QAction(
            QIcon(resource_path("add-contact.ico")), "Добавить контакт", self
        )
        self.add_contact_action.triggered.connect(self.show_add_contact_dialog)
        self.toolbar = self.addToolBar("Добавить контакт")
        self.toolbar.addAction(self.add_contact_action)
        self.delete_contact_action = QAction(
            QIcon(resource_path("delete-contact.ico")), "Удалить контакт", self
        )
        self.open_tag_table_action = QAction(
            QIcon(resource_path("open-tags.ico")), "Открыть теги", self
        )
        self.open_tag_table_action.triggered.connect(self.open_tag_table)
        self.toolbar.addAction(self.open_tag_table_action)
        self.delete_contact_action.triggered.connect(self.delete_contact)
        self.toolbar.addAction(self.delete_contact_action)
        self.edit_contact_action = QAction(
            QIcon(resource_path("edit-contact.ico")), "Редактировать контакт", self
        )
        self.edit_contact_action.triggered.connect(self.show_edit_contact_dialog)
        self.toolbar.addAction(self.edit_contact_action)
        self.populate_table()
        self.setCentralWidget(self.table)
        self.tag_table_window = None
        self.about_action = QAction(QIcon(resource_path("about-icon.png")), "О приложении", self)
        self.about_action.triggered.connect(self.show_about_dialog)
        self.toolbar.addAction(self.about_action)
        self.checkbox_container = QWidget()
        self.checkbox_layout = QVBoxLayout()
        self.checkbox_container.setLayout(self.checkbox_layout)
        self.light_theme_checkbox = QCheckBox("Светлая тема", self)
        self.dark_theme_checkbox = QCheckBox("Тёмная тема", self)
        self.light_theme_checkbox.stateChanged.connect(self.set_light_theme)
        self.dark_theme_checkbox.stateChanged.connect(self.set_dark_theme)
        self.checkbox_layout.addWidget(self.light_theme_checkbox)
        self.checkbox_layout.addWidget(self.dark_theme_checkbox)
        self.import_action = QAction(QIcon(resource_path("import-icon.png")), "Импорт контактов", self)
        self.import_action.triggered.connect(self.show_import_dialog)
        self.toolbar.addAction(self.import_action)
        self.export_action = QAction(
            QIcon(resource_path("export-icon.png")), "Экспорт контактов", self
        )
        self.export_action.triggered.connect(self.show_export_dialog)
        self.toolbar.addAction(self.export_action)
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.table)
        main_layout.addWidget(self.checkbox_container)
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.search_contact_action = QAction(
            QIcon(resource_path("search-contact.ico")), "Поиск контактов", self
        )
        self.search_contact_action.triggered.connect(self.show_search_contact_dialog)
        self.toolbar.addAction(self.search_contact_action)

    def show_import_dialog(self):
        options = QFileDialog.Options()
        """
        Ни разу не юзал до этого QFileDialog 
        в питоне, зато юзал когда писал на C++ в Qt Creator
        """
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл для импорта контактов",
            "",
            "Text Files (*.txt);;All Files (*)",
            options=options,
        )
        if file_name:
            self.import_contacts_from_file(file_name)

    def show_export_dialog(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Выберите файл для экспорта контактов",
            "",
            "Text Files (*.txt);;All Files (*)",
            options=options,
        )
        if file_name:
            self.export_contacts_to_file(file_name)

    def import_contacts_from_file(self, filename):
        with open(filename, "r", encoding="utf-8") as file:
            contacts = []
            lines = file.readlines()
            for i in range(0, len(lines), 3):
                name = lines[i].strip()
                email = lines[i + 1].strip()
                phone = lines[i + 2].strip()
                contacts.append(Contact(name, email, phone))
            for contact in contacts:
                """
                тут был ещё один забавный баг, когда я еще только дописывал это
                контакты импортированные в таблице не сохранялись
                только уже спустя часа три я догадался добавить туда эту функцию
                """
                self.insert_contact_to_db(contact)
            self.populate_table()

    def export_contacts_to_file(self, filename):
        contacts = self.read_contacts_from_db()
        with open(filename, "w", encoding="utf-8") as file:
            for contact in contacts:
                file.write(f"{contact[0]}\n{contact[1]}\n{contact[2]}\n")
                # чем не работа с файлами?)

    def set_light_theme(self, state):
        # создание светлой темы - самый простой этап проекта
        if state == Qt.Checked:
            self.dark_theme_checkbox.setChecked(False)
            qApp.setStyleSheet("")

    def set_dark_theme(self, state):
        if state == Qt.Checked:
            self.light_theme_checkbox.setChecked(False)
            dark_theme_style = """
            QMainWindow {
                background-color: #333333;
                color: #FFFFFF;
            }
            QTableWidget {
                background-color: #444444;
                color: #FFFFFF;
            }
            QTableView QTableCornerButton::section {
                color: red;
                background-color: rgb(64, 64, 64);
                border: 5px solid #f6f7fa;
                border-radius:0px;
                border-color: rgb(64, 64, 64);
            }

            QTableView {
                Color: white; 
                Gridline-color: black; 
                Background-color: rgb(108, 108, 108); 
                alternate-background-color: rgb(64, 64, 64);
                Selection-color: white; 
                Selection-background-color: rgb(77, 77, 77); 
                border: 2px groove gray;
                border-radius: 0px;
                padding: 2px 4px;
            }

            QHeaderView {
                color: white;
                font: bold 10pt;
                background-color: rgb(108, 108, 108);
                border: 0px solid rgb(144, 144, 144);
                border:0px solid rgb(191,191,191);
                border-left-color: rgba(255, 255, 255, 0);
                border-top-color: rgba(255, 255, 255, 0);
                border-radius:0px;
                min-height:29px;
            }

            QHeaderView::section {
                color: white;
                background-color: rgb(64, 64, 64);
                border: 5px solid #f6f7fa;
                border-radius:0px;
                border-color: rgb(64, 64, 64);
            } 
            """
            qApp.setStyleSheet(dark_theme_style)
            """
            Пару шаблонов скопировал вообще
            Кое-как смог исправить те поля белые, которые мне покоя не давали
            """

    def search_contacts(self, search_type, search_text):
        contacts = self.read_contacts_from_db()
        search_results = []
        for contact in contacts:
            if search_type == "Имя" and search_text in contact[0]:
                search_results.append(contact)
            elif search_type == "Почта" and search_text in contact[1]:
                search_results.append(contact)
            elif search_type == "Телефон" and search_text in contact[2]:
                search_results.append(contact)
            # поиск прекрасно работает, но единственный минус - для того чтобы снова увидеть
            # полный список контактов, нужно перезапустить приложение... не учёл я этого
            # но в целом ошибкой или багом это назвать трудно, будто бы так и задумано
        self.populate_search_table(search_results)

    def populate_search_table(self, search_results):
        self.table.setRowCount(0)
        self.table.setRowCount(len(search_results))
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Имя", "Почта", "Телефон"])
        for i, contact in enumerate(search_results):
            name_item = QTableWidgetItem(contact[0])
            email_item = QTableWidgetItem(contact[1])
            phone_item = QTableWidgetItem(contact[2])
            self.table.setItem(i, 0, name_item)
            self.table.setItem(i, 1, email_item)
            self.table.setItem(i, 2, phone_item)

    def show_search_contact_dialog(self):
        dialog = SearchContactDialog(self)
        dialog.exec_()

    def toggle_music(self):
        # музыка сама собой включается сразу при открытии приложения, поэтому
        # смысла особого в надписи на кнопке "начать воспроизведение нет
        # но её там видно буквально на миллисекунду, поэтому пусть уже будет
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def check_music_state(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.music_button.setText("Пауза")
        else:
            self.music_button.setText("Возобновить")

    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.exec_()

    def open_tag_table(self):
        if self.tag_table_window is None:
            # важная проверка, без неё по какой-то странной причине
            # приложение накрывалось медным тазом и вылетало
            self.tag_table_window = TagTableWindow()
        self.tag_table_window.show()

    def delete_contact(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            contact_name = self.table.item(current_row, 0).text()
            contact_phone = self.table.item(current_row, 1).text()
            if contact_name:
                connection = sqlite3.connect("contacts.db")
                cursor = connection.cursor()
                """
                до последнего дня эта функция удаляла ВСЕ контакты с одинаковым именем
                теперь удаляет только с одинаковым именем и номером(ну просто имя может
                быть и одинаковое, а вот номер нет... то же изменение было произведено 
                в функции удаления тегов
                """
                cursor.execute(
                    "DELETE FROM contacts WHERE name = ? and phone = ?",
                    (contact_name, contact_phone),
                )
                connection.commit()
                connection.close()

                self.table.removeRow(current_row)
            else:
                QMessageBox.critical(self, "Ошибка!", "Неизвестный контакт")
        else:
            QMessageBox.critical(self, "Ошибка", "Выберите контакт для удаления")

    def show_edit_contact_dialog(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            name = self.table.item(current_row, 0).text()
            email = self.table.item(current_row, 1).text()
            phone = self.table.item(current_row, 2).text()
            dialog = EditContactDialog(self, name, email, phone)
            if dialog.exec_() == QDialog.Accepted:
                new_contact = dialog.get_contact()
                if new_contact:
                    old_name = name
                    self.update_contact_in_db(old_name, new_contact)
                    self.populate_table()
                else:
                    QMessageBox.critical(
                        self, "Ошибка", "Одно или несколько полей пустые"
                    )
        else:
            QMessageBox.critical(self, "Ошибка", "Выберите контакт для редактирования")

    def read_contacts_from_db(self):
        connection = sqlite3.connect("contacts.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM contacts")
        contacts = cursor.fetchall()
        connection.close()
        return contacts

    def insert_contact_to_db(self, contact):
        connection = sqlite3.connect("contacts.db")
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO contacts VALUES (?, ?, ?)",
            (contact.name, contact.email, contact.phone),
        )
        connection.commit()
        connection.close()

    """
    роковая функция, которая накрывала мне редактирование
    чуть менее, чем полностью...
    а решение было куда проще чем я думал - отдельно сохранить старое имя
    и обновлять по нему, а новое уже пихать в таблицу/бд
    """

    def update_contact_in_db(self, old_name, contact):
        connection = sqlite3.connect("contacts.db")
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE contacts SET name = ?, email = ?, phone = ? WHERE name = ?",
            (contact.name, contact.email, contact.phone, old_name),
        )
        connection.commit()
        connection.close()

    def populate_table(self):
        contacts = self.read_contacts_from_db()
        self.table.setRowCount(len(contacts))
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Имя", "Почта", "Телефон"])
        for i, contact in enumerate(contacts):
            name_item = QTableWidgetItem(contact[0])
            email_item = QTableWidgetItem(contact[1])
            phone_item = QTableWidgetItem(contact[2])
            self.table.setItem(i, 0, name_item)
            self.table.setItem(i, 1, email_item)
            self.table.setItem(i, 2, phone_item)

    def show_add_contact_dialog(self):
        dialog = AddContactDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            contact = dialog.get_contact()
            if contact:
                self.insert_contact_to_db(contact)
                self.populate_table()
                if self.tag_table_window is not None:
                    self.tag_table_window.update_tag_table(contact.phone, contact.name)
            else:
                """
                Конечно можно было бы указать, какое именно
                поле является пустым, но разве это не и так видно?
                """
                QMessageBox.critical(self, "Ошибка!", "Одно или несколько полей пустые")


class SearchContactDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Поиск контакта")
        self.setWindowIcon(QIcon(resource_path("search-contact.ico")))
        self.search_label = QLabel("Поиск по:")
        """
        именно во время создания поиска мне пришло
        в голову, что можно использовать combobox
        для выбора типа поиска
        """
        self.search_combo = QComboBox()
        self.search_combo.addItems(["Имя", "Почта", "Телефон"])
        self.search_lineEdit = QLineEdit()
        self.search_button = QPushButton("Искать")
        layout = QVBoxLayout()
        layout.addWidget(self.search_label)
        layout.addWidget(self.search_combo)
        layout.addWidget(self.search_lineEdit)
        layout.addWidget(self.search_button)
        self.setLayout(layout)
        self.search_button.clicked.connect(self.search_contact)

    def search_contact(self):
        search_type = self.search_combo.currentText()
        search_text = self.search_lineEdit.text()
        self.parent().search_contacts(search_type, search_text)
        self.close()


class TagTableWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        """
        А тут тоже бардак
        """
        self.setWindowTitle("Теги")
        self.setWindowIcon(QIcon(resource_path("tags.ico")))
        self.setGeometry(600, 300, 600, 600)
        self.tag_table = QTableWidget()
        self.add_tag_action = QAction(QIcon(resource_path("add-tag.ico")), "Добавить тег", self)
        self.add_tag_action.triggered.connect(self.show_add_tag_dialog)
        self.delete_contact_action = QAction(
            QIcon(resource_path("delete-contact.ico")), "Удалить тег", self
        )
        self.delete_contact_action.triggered.connect(self.delete_tag)
        self.toolbar = self.addToolBar("Удалить тег")
        self.toolbar.addAction(self.delete_contact_action)
        self.toolbar = self.addToolBar("Добавить тег")
        self.toolbar.addAction(self.add_tag_action)
        self.setCentralWidget(self.tag_table)
        self.checkbox_container = QWidget()
        self.checkbox_layout = QVBoxLayout()
        self.checkbox_container.setLayout(self.checkbox_layout)
        self.light_theme_checkbox = QCheckBox("Светлая тема", self)
        self.dark_theme_checkbox = QCheckBox("Тёмная тема", self)
        self.light_theme_checkbox.stateChanged.connect(self.set_light_theme)
        self.dark_theme_checkbox.stateChanged.connect(self.set_dark_theme)
        self.checkbox_layout.addWidget(self.light_theme_checkbox)
        self.checkbox_layout.addWidget(self.dark_theme_checkbox)
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tag_table)
        main_layout.addWidget(self.checkbox_container)
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.populate_tag_table()

    def delete_tag(self):
        current_row = self.tag_table.currentRow()
        if current_row >= 0:
            contact_phone = self.tag_table.item(current_row, 0).text()
            contact_tags = self.tag_table.item(current_row, 1).text()
            if contact_phone:
                connection = sqlite3.connect("tags.db")
                cursor = connection.cursor()
                cursor.execute(
                    "DELETE FROM tags WHERE number = ? and tags = ?",
                    (contact_phone, contact_tags),
                )
                connection.commit()
                connection.close()
                self.tag_table.removeRow(current_row)
            else:
                QMessageBox.critical(self, "Ошибка!", "Неизвестный тег/номер")
        else:
            QMessageBox.critical(self, "Ошибка", "Выберите контакт для удаления")

    def check_number_in_db(self, number):
        connection = sqlite3.connect("contacts.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM contacts WHERE phone = ?", (number,))
        result = cursor.fetchone()
        connection.close()
        return result is not None

    """
    Эти две функции 
    insert_tag_to_db
    delete_tag
    почти идентичны тем, что в другом классе, с контактами
    """

    def insert_tag_to_db(self, number, tags):
        try:
            connection = sqlite3.connect("tags.db")
            cursor = connection.cursor()
            cursor.execute("INSERT INTO tags VALUES (?, ?)", (number, tags))
            connection.commit()
        except sqlite3.Error as e:
            print("SQLite error:", e)
        finally:
            connection.close()

    def set_light_theme(self, state):
        if state == Qt.Checked:
            self.dark_theme_checkbox.setChecked(False)
            qApp.setStyleSheet("")

    def set_dark_theme(self, state):
        if state == Qt.Checked:
            self.light_theme_checkbox.setChecked(False)
            dark_theme_style = """
            QMainWindow {
                background-color: #333333;
                color: #FFFFFF;
            }
            QTableWidget {
                background-color: #444444;
                color: #FFFFFF;
            }
            QTableView QTableCornerButton::section {
                color: red;
                background-color: rgb(64, 64, 64);
                border: 5px solid #f6f7fa;
                border-radius:0px;
                border-color: rgb(64, 64, 64);
            }

            QTableView {
                Color: white; 
                Gridline-color: black; 
                Background-color: rgb(108, 108, 108); 
                alternate-background-color: rgb(64, 64, 64);
                Selection-color: white; 
                Selection-background-color: rgb(77, 77, 77); 
                border: 2px groove gray;
                border-radius: 0px;
                padding: 2px 4px;
            }

            QHeaderView {
                color: white;
                font: bold 10pt;
                background-color: rgb(108, 108, 108);
                border: 0px solid rgb(144, 144, 144);
                border:0px solid rgb(191,191,191);
                border-left-color: rgba(255, 255, 255, 0);
                border-top-color: rgba(255, 255, 255, 0);
                border-radius:0px;
                min-height:29px;
            }

            QHeaderView::section {
                color: white;
                background-color: rgb(64, 64, 64);
                border: 5px solid #f6f7fa;
                border-radius:0px;
                border-color: rgb(64, 64, 64);
            } 
            """
            qApp.setStyleSheet(dark_theme_style)
            """
            да, дубликат из главного класса. просто чтобы было
            на всякий случай, переключает тему в обоих окнах
            """

    def show_add_tag_dialog(self):
        dialog = AddTagDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            number = dialog.get_number()
            tags = dialog.get_tags()
            if number and tags:
                if not self.check_number_in_db(number):
                    QMessageBox.critical(
                        self, "Ошибка", "Номер не найден в базе данных контактов"
                    )
                else:
                    self.insert_tag_to_db(number, tags)
                    self.insert_tag_to_table(number, tags)
            else:
                QMessageBox.critical(
                    self, "Ошибка", "Поле номера или поля тегов не заполнены"
                )

    def populate_tag_table(self):
        self.tag_table.setColumnCount(2)
        self.tag_table.setHorizontalHeaderLabels(["Номер", "Теги"])
        self.tag_table.setRowCount(0)
        tags = self.read_tags_from_db()
        for tag in tags:
            self.insert_tag_to_table(tag[0], tag[1])

    def read_tags_from_db(self):
        connection = sqlite3.connect("tags.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM tags")
        tags = cursor.fetchall()
        connection.close()
        return tags

    def insert_tag_to_table(self, number, tags):
        row_count = self.tag_table.rowCount()
        self.tag_table.insertRow(row_count)
        number_item = QTableWidgetItem(str(number))
        tags_item = QTableWidgetItem(tags)
        self.tag_table.setItem(row_count, 0, number_item)
        self.tag_table.setItem(row_count, 1, tags_item)

    def update_tag_table(self, number, tags):
        row_count = self.tag_table.rowCount()
        self.tag_table.insertRow(row_count)
        number_item = QTableWidgetItem(number)
        tags_item = QTableWidgetItem(tags)
        self.tag_table.setItem(row_count, 0, number_item)
        self.tag_table.setItem(row_count, 1, tags_item)
        self.insert_tag_to_db(number, tags)


class AddTagDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить тег")
        self.setWindowIcon(QIcon("add-tag.ico"))
        self.number_label = QLabel("Номер:")
        self.number_lineEdit = QLineEdit()
        self.tags_label = QLabel("Теги:")
        self.tags_lineEdit = QLineEdit()
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout = QFormLayout()
        layout.addRow(self.number_label, self.number_lineEdit)
        layout.addRow(self.tags_label, self.tags_lineEdit)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def get_number(self):
        number = self.number_lineEdit.text().strip()
        if number:
            return number
        else:
            return None

    def get_tags(self):
        tags = self.tags_lineEdit.text().strip()
        if tags:
            return tags
        else:
            return None

    """
    Интересное замечание - если бы была функция редактировать тег,
    то была бы та же проблема что и с редактированием контактов - скорее всего
    поле "номер" бы не редактировалось и пришлось сохранять старый номер отдельно...
    но какой смысл вообще его редактировать? тег он на то и тег...
    """


if __name__ == "__main__":
    app = QApplication(sys.argv)
    connection = sqlite3.connect("contacts.db")
    cursor = connection.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS contacts (name TEXT, email TEXT, phone TEXT)"
    )
    """
    Гораздо умнее было бы создать поле ID которому бы автоматом присваивалось 
    число, которое потом бы увеличивалось автоматически с каждой
    записью в базе данных
    но додумался я об этом только когда почти всё было дописано и интегрировать ещё одно дополнительное поле
    пришлось бы вероятно переписывать больше половины всего проекта
    """
    connection.close()
    connection = sqlite3.connect("tags.db")
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS tags (number TEXT, tags TEXT)")
    connection.close()
    window = ContactsMainWindow()
    screen = app.primaryScreen()
    rect = screen.availableGeometry()
    window.setMaximumSize(rect.size())
    window.show()
    sys.exit(app.exec_())
