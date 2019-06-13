import re
import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

from ep2_tool.test_group import TestGroup
from ep2_tool.ui.mainwindow import Ui_MainWindow
from ep2_tool.group_infos import GroupInfos
from ep2_tool.settings import Settings
from ep2_tool.dialog.settingsdialog import SettingsDialog
from ep2_tool.git_interactions import GitInteractions
from ep2_tool.dialog.gitdialog import GitDialog
from ep2_tool.group import Group
from ep2_tool.dialog.create_csv import CreateCSVDialog
from ep2_tool.ep2_tutors.common import *
from ep2_tool.dialog.test_mode_dialog import TestModeDialog
from os import path


class PkToolMainWindow(QMainWindow, Ui_MainWindow):
    """
    Application which allows to manage the csv-attendance-files from the pk-repo.
    """

    def __init__(self):
        """
        Initialize everything. Connect signals and slots. Read repo.
        """
        self.config = create_config()

        if path.exists(path.join(tutor_repo(self.config), 'tests')):
            dialog = TestModeDialog()
            result = dialog.exec_()
            if result == 1:
                self.mode = GuiMode.Test
            else:
                self.mode = GuiMode.Exercise
        else:
            self.mode = GuiMode.Exercise

        self.dir = tutor_repo(self.config) if self.mode == GuiMode.Exercise else path.join(tutor_repo(self.config),
                                                                                           'tests')

        QMainWindow.__init__(self)
        self.setupUi(self, self.mode)

        self.group_infos = GroupInfos(repo_path='')
        self.csv_files = dict()
        self.test_group = None

        self.settings = Settings()
        self.git_interactions = GitInteractions(self.settings, self.action_commit_and_push)

        self.file_combobox.currentIndexChanged.connect(self.load_group_data)
        self.group_combobox.currentIndexChanged.connect(self.populate_files)
        # self.group_type_combobox.currentIndexChanged.connect(self.fill_group_names_combobox)
        self.console.returnPressed.connect(self.execute_console)
        self.action_new.triggered.connect(self.new_csv)
        self.action_undo.triggered.connect(self.table_widget.undo_history)
        self.action_redo.triggered.connect(lambda: self.table_widget.undo_history(True))
        self.action_about.triggered.connect(self.show_about)
        self.action_settings.triggered.connect(self.open_settings)
        self.action_get_email.triggered.connect(self.get_email)
        self.action_commit_and_push.triggered.connect(self.open_git_dialog)
        self.action_load_test_applications.triggered.connect(self.open_load_test_mode)

        self.read_repo()
        if not self.settings.repo_path:
            self.open_settings()

        if self.mode == GuiMode.Test:
            self.label_group.setText("Test")
            self.label_file.setText("Slot")

    def show_about(self):
        """
        Opens a messagebox that shows informations about this application.
        """
        QMessageBox.about(self, 'About', 'https://github.com/jakobkogler/pk-tool')

    def open_settings(self):
        """
        Opens the settings-dialog, which allows to define the path to the pk-repo and the username.
        Updates everything after closing.
        """
        settings_dialog = SettingsDialog(self.settings)
        settings_dialog.exec_()
        self.read_repo()

    def open_git_dialog(self):
        """
        Open a dialog for commiting files to git.
        """
        if self.settings.use_git:
            git_dialog = GitDialog(self.git_interactions)
            git_dialog.exec_()

    def open_load_test_mode(self):
        """
        Opens a dialog that allows to load a registration file for a test and loads the test attendance csv-files.
        """
        pass

    def test_mode(self, int):
        print(int)

    def read_repo(self):
        """
        Read all important data from the pk-repo and fill all comboboxes accordingly
        """
        self.git_interactions.pull_and_react()
        self.group_infos = GroupInfos(repo_path=self.settings.repo_path)
        self.table_widget.connect(self.group_infos, self.action_undo, self.action_redo,
                                  self.get_csv_path, self.write_console)

        self.fill_group_names_combobox()

    def write_console(self, text):
        """
        Write a text to the console.
        """
        self.console_output.setText(text)

    def fill_group_names_combobox(self):
        """
        Populate the combobox with all the group names, that apply for the group type specified in the form.
        """
        group_names = sorted([o for o in os.listdir(self.dir)
                              if os.path.isdir(os.path.join(self.dir, o)) and o != '.git'
                              and o != 'templates' and o != 'Stundenlisten' and o != 'Erfahrungsbericht'
                              and o != 'tests'])

        if group_names:
            self.group_combobox.currentIndexChanged.disconnect()

            self.group_combobox.clear()

            self.group_combobox.addItems(group_names)

            self.group_combobox.currentIndexChanged.connect(self.populate_files)
            self.populate_files()

    def load_group_data(self):
        """
        Load all data for a specific group.
        It updates the names of the instructor and tutors and loads the last available csv-file for this group.
        """
        group_name = self.group_combobox.currentText()
        # try:
        #     info = self.group_infos.get_group_info(group_name)
        #     self.label_instructor_name.setText(info.instructor)
        #     self.label_tutor1_name.setText(info.tutor1)
        #     self.label_tutor2_name.setText(info.tutor2)
        # except KeyError:
        #     pass

        group = Group(group_name, self.config,
                      student_info(self.config, group_name)) if self.mode == GuiMode.Exercise else self.test_group
        # if self.group_type_combobox.currentIndex() == 4:
        #     group = Group(self.file_combobox.currentText())

        # ue = re.findall('attendance_(\\d*).csv', )[0]

        self.table_widget.setup_table(group, self.file_combobox.currentText())
        # if self.file_combobox.count():
        #    self.table_widget.load_csv_file(self.get_csv_path(), False)
        # else:
        #    self.table_widget.clear()

    def get_email(self):
        """
        Determine all email-adresses from the current group and push the into the clipboard.
        """
        clipboard = QApplication.clipboard()
        group_name = self.group_combobox.currentText()
        group = self.group_infos.get_group_info(group_name)
        emails = [student.email for student in group.students]
        clipboard.setText(', '.join(emails))

    def get_csv_path(self):
        """
        Returns the path to the current csv-file
        """
        return self.csv_files[self.file_combobox.currentText()]

    def new_csv(self):
        """
        Generate a new csv-file for this group.
        """
        create_csv_dialog = CreateCSVDialog(self.settings, self.group_combobox.currentText())
        create_csv_dialog.exec_()

        if create_csv_dialog.selected_file:
            self.populate_files()
            index = self.file_combobox.count() - 1
            for i in range(self.file_combobox.count()):
                if create_csv_dialog.selected_file == self.file_combobox.itemText(i):
                    index = i
            self.file_combobox.setCurrentIndex(index)

    def populate_files(self):
        """
        Finds the csv files for this group and populates the combobox
        """
        group_name = self.group_combobox.currentText()
        self.file_combobox.clear()

        if self.mode == GuiMode.Test:
            self.test_group = TestGroup(group_name, self.config, test_student_info(self.config, group_name))

        regex = 'attendance_(\\d*).csv' if self.mode == GuiMode.Exercise else '(.+_slot\\d+)\\.csv'

        files = sorted([re.findall(regex, o)[0]
                        for o in os.listdir(os.path.join(self.dir, group_name))
                        if os.path.isfile(os.path.join(self.dir, group_name, o))
                        and re.match(regex, o)])
        self.file_combobox.addItems(files)
        self.file_combobox.setCurrentIndex(self.file_combobox.count() - 1)
        self.file_combobox.currentIndexChanged.connect(self.load_group_data)
        self.load_group_data()

    def get_test_files(self, test_folder):
        path = self.settings.repo_path + '/Anwesenheiten/Tests/' + test_folder + '/'
        return {name.rstrip('.csv'): os.path.join(root, name)
                for root, dirs, files in os.walk(path)
                for name in files
                if name.endswith('.csv')}

    def get_csv_files(self, group_name):
        path = self.settings.repo_path + '/Anwesenheiten/Uebungen/'
        return {os.path.basename(root): os.path.join(root, name)
                for root, dirs, files in os.walk(path)
                for name in files
                if name.startswith(group_name)
                if name != 'placeholder'}

    def execute_console(self):
        """
        Executes a command from the console
        'name a' checks the attendance
        'name b' unchecks the attendance
        'name number' writes the adhoc-points
        'name other' writes a comment
        """
        try:
            commands = self.console.text().split(' ')
            identification, command = commands[0], ' '.join(commands[1:])
            index = self.table_widget.index_of_student(identification)
            if index >= 0:
                if command == 'a':
                    self.table_widget.get_checkbox(index).setCheckState(QtCore.Qt.Checked)
                elif command == 'b':
                    self.table_widget.get_checkbox(index).setCheckState(QtCore.Qt.Unchecked)
                elif command.isdigit():
                    self.table_widget.item(index, 4).setText(command)
                else:
                    self.table_widget.item(index, 5).setText(command)
            else:
                if index == -1:
                    error = 'Der Student "{}" wurde nicht gefunden.'
                else:
                    error = 'Mehrere Studenten treffen auf "{}" zu.'
                self.write_console('Error: ' + error.format(identification))
        except IndexError:
            pass

        self.console.clear()


def main():
    app = QApplication(sys.argv)
    window = PkToolMainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
