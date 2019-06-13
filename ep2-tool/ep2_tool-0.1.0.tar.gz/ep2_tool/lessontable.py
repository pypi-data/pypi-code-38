from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QWidget, QCheckBox, QHBoxLayout
from ep2_tool.group import Group, AttendanceType, attendance_csv_fieldnames, KEY_UE_ATTENDED
from ep2_tool.history import History
from ep2_tool.ep2_tutors.common import *
from ep2_tool.test_group import test_attendance_csv_fieldnames, KEY_TEST_ATTENDED


class LessonTable(QTableWidget):
    """
    Extent the QTableWidget, so that it can maintain the date in the table.
    This includes filling the table with data using the name of a group and a corresponding csv-file,
    recording every change in a history, and exporting the data back to a csv-file.

    Usage infos: after creating the table the method connect has to be called!
    """

    def __init__(self, widget, mode=GuiMode.Exercise):
        """
        Initialize locks and history data. Connect signals and slots.
        """
        super().__init__(widget)

        self.react_lock = False
        self.history = History()
        self.group_infos = None
        self.action_redo = None
        self.action_undo = None
        self.get_csv_path = None
        self.group = None
        self.write_console = None
        self.test_file = False
        self.current_ue = None
        self.mode = mode

        self.cellChanged.connect(self.react_to_change)

    def connect(self, group_infos, action_undo, action_redo, get_csv_path, write_console):
        """
        Connect infos and important actions from the mainwindow with the table.
        """
        self.group_infos = group_infos
        self.action_undo = action_undo
        self.action_redo = action_redo
        self.get_csv_path = get_csv_path
        self.write_console = write_console

    def react_to_change(self):
        """
        React if there are no locks by writing the changes to history and by exporting the data to the csv-file.
        Change the count of the attendance column.
        """
        if not self.react_lock:
            # self.history.record_changes(self.get_current_data())
            self.export_csv()

            count = sum(self.get_checkbox(index).checkState() == Qt.Checked for index in range(self.rowCount()))
            attendance = 'Anwesend {}/{}'.format(count, self.rowCount())
            self.setHorizontalHeaderItem(3, QTableWidgetItem(attendance))

            # self.history.adjust_undo_redo()

    def setup_table(self, group, ue):
        """
        Clear the table and history, refill the table with column names, and students default data.
        """

        if ue == '':
            return

        self.react_lock = True
        self.current_ue = ue

        self.clear()
        self.setRowCount(0)

        self.group = group
        labels = 'Nachname;Vorname;Matrikelnr.;Anwesend 00/00'.split(';')
        self.setColumnCount(len(labels))
        self.setSortingEnabled(False)
        self.setHorizontalHeaderLabels(labels)

        students = group.get_students(ue)

        for student in students:
            self.add_row_to_table(group, students[student])

        self.history = History(self.action_undo, self.action_redo, self.write_console, self.group_infos)

        self.setSortingEnabled(True)
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.resizeColumnsToContents()

        self.react_lock = False
        self.react_to_change()

    def add_row_to_table(self, group, student):
        """
        Adds a new row to the table and fills this row with item-widgets filled with the student's data.
        """
        idx = self.rowCount()
        self.setRowCount(idx + 1)

        last_name_item = QTableWidgetItem(student[KEY_STUDENT_NAME_LAST])
        last_name_item.setFlags(last_name_item.flags() & ~QtCore.Qt.ItemIsEditable)
        self.setItem(idx, 0, last_name_item)

        first_name_item = QTableWidgetItem(student[KEY_STUDENT_NAME_FIRST])
        first_name_item.setFlags(first_name_item.flags() & ~QtCore.Qt.ItemIsEditable)
        self.setItem(idx, 1, first_name_item)

        matrikelnr_item = QTableWidgetItem(student[KEY_STUDENT_ID])
        matrikelnr_item.setFlags(matrikelnr_item.flags() & ~QtCore.Qt.ItemIsEditable)
        matrikelnr_item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.setItem(idx, 2, matrikelnr_item)

        check_item = QTableWidgetItem()
        check_item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.setItem(idx, 3, check_item)
        check_widget = QWidget()
        chk_bx = QCheckBox()

        attendance = group.attended(student[KEY_STUDENT_ID], self.current_ue)

        if attendance == AttendanceType.ATTENDED:
            chk_bx.setCheckState(QtCore.Qt.Checked)
        elif attendance == AttendanceType.ABSENT:
            chk_bx.setCheckState(QtCore.Qt.Unchecked)
        else:
            chk_bx.setCheckState(QtCore.Qt.PartiallyChecked)

        chk_bx.stateChanged.connect(self.react_to_change)
        lay_out = QHBoxLayout(check_widget)
        lay_out.addWidget(chk_bx)
        lay_out.setAlignment(QtCore.Qt.AlignCenter)
        lay_out.setContentsMargins(0, 0, 0, 0)
        check_widget.setLayout(lay_out)
        self.setCellWidget(idx, 3, check_widget)

    def get_checkbox(self, index):
        """
        Returns the checkbox for a specific index
        """
        return self.cellWidget(index, 3).layout().itemAt(0).widget()

    def export_csv(self):
        """
        Write the opened table to a csv-file
        """
        ue = self.current_ue
        att_csv_file = attendance_csv(self.group.config, self.group.name, ue) if self.mode == GuiMode.Exercise else \
            test_attendance_csv(self.group.config, self.group.name, ue)

        fieldnames = attendance_csv_fieldnames(ue) if self.mode == GuiMode.Exercise else \
            test_attendance_csv_fieldnames(self.group.name)

        with open(att_csv_file, 'w') as outfile:
            if six.PY2:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames, encoding='utf-8',
                                        lineterminator='\n')
            else:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames, lineterminator='\n')

            writer.writeheader()

            for idx in range(self.rowCount()):
                student_id = self.item(idx, 2).text()
                if self.get_checkbox(idx).checkState() == Qt.Checked:
                    attended = '1'
                elif self.get_checkbox(idx).checkState() == Qt.Unchecked:
                    attended = '0'
                elif self.get_checkbox(idx).checkState() == Qt.PartiallyChecked:
                    attended = '_'

                self.group.attendance[ue][student_id] = attended

                writer.writerow({KEY_STUDENT_ID: student_id, (KEY_UE_ATTENDED % ue if self.mode == GuiMode.Exercise else
                                                              KEY_TEST_ATTENDED % self.group.name): attended})

    def index_of_student(self, identification):
        """
        Find the index of a student in the table. Identification can be a part of his name or the matrikel-nummer.
        Returns -1, if no student is found, or -2 if multiple students are found.
        """
        indices = [i for i in range(self.rowCount())
                   if identification.lower() in self.item(i, 0).text().lower() or
                   identification == self.item(i, 1).text()]
        if len(indices) == 1:
            return indices[0]
        if indices:
            return -2
        else:
            return -1

    def get_current_data(self):
        """
        Reads all data from the table and returns a list of it
        """
        data = []
        for idx in range(self.rowCount()):
            if self.item(idx, 1).text():
                data.append((
                    self.item(idx, 1).text(),
                    self.item(idx, 2).text() or '0',
                    'an' if self.get_checkbox(idx).isChecked() else 'ab',
                    self.item(idx, 4).text() or '0',
                    self.item(idx, 5).text()
                ))
        return sorted(data)

    def undo_history(self, reverse=False):
        """
        Undos/redos the last history.
        """
        self.react_lock = True
        self.setSortingEnabled(False)

        last_history = self.history.undo_history(reverse=reverse)
        if last_history:
            index = self.index_of_student(last_history[0])
            if index >= 0:
                if last_history[2] == 1:
                    if not last_history[3]:
                        self.removeRow(index)

                if last_history[2] == 2:
                    self.get_checkbox(index).setCheckState(QtCore.Qt.Checked if last_history[3] == 'an' else
                                                           QtCore.Qt.Unchecked)
                if last_history[2] in [3, 4]:
                    self.item(index, last_history[2] + 1).setText(last_history[3])
            else:
                if last_history[2] == 1 and last_history[3]:
                    self.add_row_to_table(last_history[3])

            self.history.current_data = self.get_current_data()
            self.history.adjust_undo_redo()

        self.setSortingEnabled(True)
        self.react_lock = False
        self.export_csv()
