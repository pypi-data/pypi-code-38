from unittest import TestCase
from restclients_core.exceptions import (
    DataFailureException, InvalidEmployeeID, InvalidRegID, InvalidNetID)
from uw_hrp.worker import (
    get_worker_by_netid, get_worker_by_employee_id, get_worker_by_regid)
from uw_hrp.util import fdao_hrp_override


@fdao_hrp_override
class WorkerTest(TestCase):

    def test_get_worker_by_netid(self):
        self.assertRaises(DataFailureException,
                          get_worker_by_netid,
                          "None")
        self.assertRaises(InvalidNetID,
                          get_worker_by_netid,
                          "")
        worker = get_worker_by_netid("faculty")
        # self.maxDiff = None
        self.assertEqual(
            worker.to_json(),
            {"netid": "faculty",
             "regid": "10000000000000000000000000000005",
             "employee_id": "000000005",
             "employee_status": {
                 "end_emp_date": None,
                 "hire_date": "2006-05-16 07:00:00+00:00",
                 "is_active": True,
                 "is_retired": False,
                 "is_terminated": False,
                 "retirement_date": None,
                 "status": "Active",
                 "status_code": "A",
                 "termination_date": None},
             "primary_manager_id": "100000015",
             "active_positions": [{
                 "start_date": "2012-07-01 00:00:00+00:00",
                 "end_date": None,
                 "ecs_job_cla_code_desc": "Academic Personnel",
                 'fte_percent': 0.0,
                 'is_future_date': False,
                 "is_primary": True,
                 "location": "Seattle Campus",
                 "payroll_unit_code": "00753",
                 "pos_type": "Unpaid_Academic",
                 "pos_time_type_id": "Part_time",
                 "title": "Clinical Associate Professor",
                 "supervisor_eid": "100000015",
                 "job_profile": {
                     "job_code": "21184",
                     "description": "Unpaid Academic"},
                 "supervisory_org": {
                     "budget_code": "3040111000",
                     "org_code": "SOM",
                     "org_name": "Family Medicine: Volunteer"}}]})
        self.assertIsNotNone(str(worker))
        self.assertEqual(
            worker.primary_position.to_json(),
            {"start_date": "2012-07-01 00:00:00+00:00",
             "end_date": None,
             "ecs_job_cla_code_desc": "Academic Personnel",
             'fte_percent': 0.0,
             'is_future_date': False,
             "is_primary": True,
             "location": "Seattle Campus",
             'payroll_unit_code': '00753',
             "pos_type": "Unpaid_Academic",
             "pos_time_type_id": "Part_time",
             "title": "Clinical Associate Professor",
             "supervisor_eid": "100000015",
             "job_profile": {
                 "job_code": "21184",
                 "description": "Unpaid Academic"},
             "supervisory_org": {
                 "budget_code": "3040111000",
                 "org_code": "SOM",
                 "org_name": "Family Medicine: Volunteer"}})
        self.assertEqual(len(worker.other_active_positions), 0)

        worker = get_worker_by_netid("faculty", current_future=False)
        self.assertIsNotNone(worker)

    def test_get_worker_by_employee_id(self):
        worker = get_worker_by_employee_id("100000015")
        self.assertTrue(worker.netid, 'chair')

        worker = get_worker_by_employee_id("100000015", current_future=False)
        self.assertIsNotNone(worker)

        self.assertRaises(InvalidEmployeeID,
                          get_worker_by_employee_id,
                          "")

    def test_get_worker_by_regid(self):
        worker = get_worker_by_regid("10000000000000000000000000000015")
        self.assertTrue(worker.netid, 'chair')

        worker = get_worker_by_regid("10000000000000000000000000000015",
                                     current_future=False)
        self.assertIsNotNone(worker)

        self.assertRaises(DataFailureException,
                          get_worker_by_regid,
                          "00000000000000000000000000000001")
        self.assertRaises(InvalidRegID,
                          get_worker_by_regid, "000")
