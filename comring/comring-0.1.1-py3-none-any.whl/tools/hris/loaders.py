from xlrd import open_workbook
import logging
import pprint

LOGGER = logging.getLogger(__name__)

PP = pprint.PrettyPrinter(indent=4)

def pfdebug(logger, data):
    for line in PP.pformat(data).split('\n'):
        logger.debug(line)

class Loader(object):
    def __init__(self):
        pass

    def load(self, file_name):
        return False

    def get_total_names(self):
        return []

    def get_total(self, name):
        return 0

class XLSLoader(Loader):
    def __init__(self):
        self.next_is_head2 = False
        self.next_is_detail = False

        self.head1 = {}
        self.head2 = {}
        self.grand_total = {}
        self.detail_dept = {}

    def _identify_head1(self, row_index, cells):
        res = self.head1
        col_index = 0
        for cell in cells:
            if cell.value == "Department":
                res["department"] = {"col_index": col_index}
            if cell.value == "Allowance":
                res["allowance"] = {"col_index": col_index}
            if cell.value == "Total Income":
                res["total_income"] = {"col_index": col_index}
            if cell.value == "Tax Allowance":
                res["tax_allowance"] = {"col_index": col_index}
            if cell.value == "Deduction":
                res["deduction"] = {"col_index": col_index}
            if cell.value == "Total Deduction":
                res["total_deduction"] = {"col_index": col_index}
            if cell.value == "Tax":
                res["tax"] = {"col_index": col_index}
            if cell.value == "Net Salary":
                res["net_salary"] = {"col_index": col_index}
            col_index += 1
        return res

    def _head1_col_index(self, name):
        col_info = self.head1.get(name, None)
        if col_info:
            return col_info.get("col_index", -1)
        return -1

    def _add_head2(self, cells, start, length, name=""):
        col_idx = start
        count = 0
        while count < length:
            if not name:
                col_name = cells[col_idx+count].value
            else:
                col_name = name
            self.head2[col_name] = {"col_idx": col_idx+count}
            count += 1

    def _identify_head2(self, row_index, cells):
        res = {}
        allowance_ci = self._head1_col_index("allowance")
        total_income_ci = self._head1_col_index("total_income")
        tax_allowance_ci = self._head1_col_index("tax_allowance")
        deduction_ci = self._head1_col_index("deduction")
        total_deduction_ci = self._head1_col_index("total_deduction")
        tax_ci = self._head1_col_index("tax")
        net_salary_ci = self._head1_col_index("net_salary")

        if allowance_ci > -1 and total_income_ci > -1:
            self._add_head2(cells, allowance_ci, total_income_ci-allowance_ci)
        if total_income_ci > -1:
            self._add_head2(cells, total_income_ci, 1, name="Total Income")

        if tax_allowance_ci > -1:
            self._add_head2(cells, tax_allowance_ci, 1, name="Tax Allowance")

        if deduction_ci > -1 and total_deduction_ci > -1:
            self._add_head2(cells, deduction_ci, total_deduction_ci-deduction_ci)
        if total_deduction_ci > -1:
            self._add_head2(cells, total_deduction_ci, 1, name="Total Deduction")

        if tax_ci > -1:
            self._add_head2(cells, tax_ci, 1, name="Tax")

        if net_salary_ci > -1:
            self._add_head2(cells, net_salary_ci, 1, name="Net Salary")

        return res

    def _identify_grand_totals(self, row_index, cells):
        for key in self.head2.keys():
            col = self.head2.get(key).get("col_idx", -1)
            total = 0
            if col > -1:
                total = cells[col].value
            self.grand_total[key] = total

    def _sum_detail_dept(self, dept, key, value):
        dept_data = self.detail_dept.get(dept, {})
        dept_data[key] = dept_data.get(key, 0) + value
        self.detail_dept[dept] = dept_data
        return dept_data

    def _identify_detail_row(self, row_index, cells):
        dept = cells[self._head1_col_index("department")].value
        if dept:
            for key in self.head2.keys():
                col = self.head2.get(key).get("col_idx", -1)
                if col > -1:
                    value = cells[col].value
                    self._sum_detail_dept(dept, key, value)

    def _identify_row(self, row_index, cells):
        if self.next_is_head2:
            self._identify_head2(row_index, cells)
            self.next_is_head2 = False
            self.next_is_detail = True
            return

        if cells[0].value == "No":
            self._identify_head1(row_index, cells)
            self.next_is_head2 = True
            return

        if self.next_is_detail and len(cells) > 7:
            self._identify_detail_row(row_index, cells)
            return

        if cells[0].value == "Grand Total:":
            self._identify_grand_totals(row_index, cells)
            self.next_is_detail = False

    def _identify_data(self, sheet):
        row_idx = 0
        self.next_is_head2 = False
        self.next_is_detail = False
        for row in sheet.get_rows():
            self._identify_row(row_idx, row)
            row_idx += 1

    def _process_sheet(self, sheet):
        LOGGER.debug("Processing sheet %s", sheet.name)
        self._identify_data(sheet)
        pfdebug(LOGGER, self.head1)
        pfdebug(LOGGER, self.head2)
        pfdebug(LOGGER, self.grand_total)

    def load(self, file_name):
        wb = open_workbook(file_name)

        head_row = -1
        total_row = -1

        for sheet in wb.sheets():
            self._process_sheet(sheet)
        return True

    def get_total_names(self):
        return self.grand_total.keys()

    def get_total(self, name, default=0):
        return self.grand_total.get(name, default)

