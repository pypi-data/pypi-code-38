# coding=utf-8
from ep2_tool.ep2_tutors.common import *

if six.PY2:
    import unicodecsv as csv
else:
    import csv

KEY_TEST_ATTENDED = 'tests/%s/attended'


def test_attendance_csv_fieldnames(ue):
    return [KEY_STUDENT_ID, KEY_TEST_ATTENDED % ue]


class TestGroup:
    """
    Represent a group of students. Stores the names of the instructor and the tutors,
    and all the names, register-numbers and e-mails from students.
    """

    def __init__(self, test, config, students):
        """
        Initializes a group
        """
        self.name = test
        self.attendance = {}
        self.config = config
        self.slots = {}
        self.students = students

    def attended(self, student_id, slot):
        if slot not in self.attendance:
            attendance_csv_file = test_attendance_csv(self.config, self.name, slot)
            self.attendance[slot] = {}
            with open(attendance_csv_file, 'r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile, test_attendance_csv_fieldnames(self.name), KEY_INVALID, strict=True)

                headers = next(reader, None)
                if not validate_headers(headers):
                    print("Invalid headers: ", headers)
                    exit(1)

                for row in reader:
                    self.attendance[slot][row[KEY_STUDENT_ID]] = row[KEY_TEST_ATTENDED % self.name]

        if student_id not in self.attendance[slot]:
            return AttendanceType.NOT_SET

        if self.attendance[slot][student_id] == '1':
            return AttendanceType.ATTENDED
        elif self.attendance[slot][student_id] == '0':
            return AttendanceType.ABSENT
        else:
            return AttendanceType.NOT_SET

    def get_students(self, slot):
        if slot not in self.slots:
            attendance_csv_file = test_attendance_csv(self.config, self.name, slot)
            self.slots[slot] = {}
            with open(attendance_csv_file, 'r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile, test_attendance_csv_fieldnames(self.name), KEY_INVALID, strict=True)

                headers = next(reader, None)
                if not validate_headers(headers):
                    print("Invalid headers: ", headers)
                    exit(1)

                for row in reader:
                    self.slots[slot][row[KEY_STUDENT_ID]] = row

        result = {}
        for student in self.slots[slot]:
            result[student] = self.students[student]

        return result



