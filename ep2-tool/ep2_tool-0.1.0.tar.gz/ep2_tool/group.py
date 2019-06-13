# coding=utf-8
from ep2_tool.ep2_tutors.common import *

if six.PY2:
    import unicodecsv as csv
else:
    import csv

KEY_UE_ATTENDED = 'ue/%s/attended'


def attendance_csv_fieldnames(ue):
    return [KEY_STUDENT_ID, KEY_UE_ATTENDED % ue]


class Group:
    """
    Represent a group of students. Stores the names of the instructor and the tutors,
    and all the names, register-numbers and e-mails from students.
    """

    def __init__(self, name, config, students=None):
        """
        Initializes a group
        """
        self.name = name
        self.students = students if students else []
        self.attendance = {}
        self.config = config

    def add_student(self, student):
        """
        Adds a student to the group
        """
        self.students.append(student)

    def attended(self, student_id, ue):
        if ue not in self.attendance:
            attendance_csv_file = attendance_csv(self.config, self.name, ue)
            self.attendance[ue] = {}
            with open(attendance_csv_file, 'r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile, attendance_csv_fieldnames(ue), KEY_INVALID, strict=True)

                headers = next(reader, None)
                if not validate_headers(headers):
                    print("Invalid headers: ", headers)
                    exit(1)

                for row in reader:
                    self.attendance[ue][row[KEY_STUDENT_ID]] = row[KEY_UE_ATTENDED % ue]

        if student_id not in self.attendance[ue]:
            return AttendanceType.NOT_SET

        if self.attendance[ue][student_id] == '1':
            return AttendanceType.ATTENDED
        elif self.attendance[ue][student_id] == '0':
            return AttendanceType.ABSENT
        else:
            return AttendanceType.NOT_SET

    def get_students(self, _):
        return self.students
