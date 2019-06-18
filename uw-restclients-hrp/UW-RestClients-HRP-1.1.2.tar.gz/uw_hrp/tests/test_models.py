from unittest import TestCase
from datetime import datetime, timedelta, timezone
from uw_hrp.models import (
    EmploymentStatus, JobProfile, SupervisoryOrganization,
    Worker, WorkerPosition, parse_date)
from uw_hrp.util import fdao_hrp_override


@fdao_hrp_override
class WorkerTest(TestCase):

    def test_parse_date(self):
        self.assertIsNotNone(parse_date("2017-09-16T07:00:00.000Z"))

    def test_employment_status(self):
        emp_status = EmploymentStatus(status="Active",
                                      status_code='A')
        self.assertIsNotNone(str(emp_status))

        emp_status = EmploymentStatus(
            data={"IsActive": False,
                  "EmployeeStatus": "Terminated",
                  "EmployeeStatusCode": "N",
                  "IsTerminated": True,
                  "IsRetired": False,
                  "EndEmploymentDate": "2017-09-16T07:00:00.000Z",
                  "HireDate": "1980-07-01T07:00:00.000Z",
                  "RetirementDate": "2017-09-16T07:00:00.000Z",
                  "TerminationDate": "2017-09-16T07:00:00.000Z"})
        self.assertIsNotNone(str(emp_status))
        self.assertTrue(emp_status.is_terminated)
        self.assertFalse(emp_status.is_active)
        self.assertEqual(
            emp_status.to_json(),
            {'end_emp_date': '2017-09-16 07:00:00+00:00',
             'hire_date': '1980-07-01 07:00:00+00:00',
             'is_active': False,
             'is_retired': False,
             'is_terminated': True,
             'retirement_date': '2017-09-16 07:00:00+00:00',
             'status': 'Terminated',
             'status_code': 'N',
             'termination_date': '2017-09-16 07:00:00+00:00'})

    def test_job_profile(self):
        job_prof = JobProfile(job_code="1", description="A")
        self.assertIsNotNone(str(job_prof))

    def test_supervisory_organization(self):
        super_org = SupervisoryOrganization(
            budget_code="3010105000",
            org_code="HSA:",
            org_name="EHS: Occl Health - Acc Prevention")
        self.assertIsNotNone(str(super_org))

    def test_worker_position(self):
        # self.maxDiff = None
        pos = WorkerPosition()
        self.assertIsNotNone(str(pos))
        data = {
            "PositionBusinessTitle": "Program Operations Specialist (E S 8)",
            "PositionSupervisor": {
                "EmployeeID": "000000005",
                "Href": "/hrp/v2/worker/000000005.json"},
            "PositionTimeTypeID": "Full_time",
            "PositionTitle": "Operations Specialist (E S 8)",
            "SupervisoryOrganization": {
                "AcademicUnitID": None,
                "Code": "HSA: ",
                "ID": "HSA_000204",
                "Name": "EHS: Occl Health - Acc Prevention",
                "Description": "HSA: ENV Health & Safety: ...",
                "Href": "/hrp/v2/organization/HSA_000204.json",
                "CostCenter": {
                    "Description": "ENV HEALTH & SAFETY",
                    "ID": "015020",
                    "OrganizationCode": "3010105000",
                    "OrganizationDescription": "ENV HEALTH & SAFETY"}},
            "PositionID": "PN-0025953",
            "PositionEffectiveDate": "1994-10-01T07:00:00.000Z",
            "IsPrimaryPosition": True,
            "PositionStartDate": "1994-10-01T00:00:00.000Z",
            "PositionEndDate": "1997-10-01T00:00:00.000Z",
            "PositionType": "Regular",
            "PositionFTEPercent": "100.00000",
            "PayRateType": "Salary",
            "TotalBasePayAmount": "6066.00000",
            "TotalBasePayFrequency": "Monthly",
            "WorkShift": "First Shift",
            "ServicePeriodID": "12",
            "ServicePeriodDescription": "Service_Period_12.00",
            "JobProfileSummary": {
                "JobProfileDescription": "Operations Specialist (E S 8)",
                "JobProfileID": "11541",
                "Href": "/hrp/v2/jobProfile/11541.json",
                "JobCategory": "Professional Staff & Librarians",
                "JobFamilies": [
                    {"JobFamilyName": "01 - Staff - Professional Staff",
                     "JobFamilyID": "Professional",
                     "JobFamilySummary": None}]},
            "CostCenter": {
                "Description": "ENV HEALTH & SAFETY",
                "ID": "015020",
                "OrganizationCode": "3010105000",
                "OrganizationDescription": "ENV HEALTH & SAFETY"},
            "EcsJobClassificationCode": "E",
            "EcsJobClassificationCodeDescription": "Professional Staff",
            "ObjectCode": "01",
            "SubObjectCode": "70",
            "PayrollUnitCode": "00702",
            "IsOnLeaveFromPosition": False,
            "IsFutureDate": False,
            "IsMedicalCenterPosition": False,
            "PlannedDistributions": {
                "PlannedCompensationAllocations": [],
                "PeriodActivityAssignments": []},
            "Location": {"ID": "Seattle Campus",
                         "Name": "Seattle Campus"},
            "FutureTransactions": []}

        work_position = WorkerPosition(data=data)
        self.assertEqual(
            work_position.to_json(),
            {
                "start_date": "1994-10-01 00:00:00+00:00",
                "end_date": "1997-10-01 00:00:00+00:00",
                "ecs_job_cla_code_desc": "Professional Staff",
                "fte_percent": 100.0,
                'is_future_date': False,
                "is_primary": True,
                "location": "Seattle Campus",
                "payroll_unit_code": "00702",
                "pos_type": "Regular",
                "pos_time_type_id": "Full_time",
                "title": "Program Operations Specialist (E S 8)",
                "supervisor_eid": "000000005",
                "job_profile": {
                    "job_code": "11541",
                    "description": "Operations Specialist (E S 8)"},
                "supervisory_org": {
                    "budget_code": "3010105000",
                    "org_code": "HSA:",
                    "org_name": "EHS: Occl Health - Acc Prevention"}})
        self.assertFalse(work_position.is_active_position())
        self.assertIsNotNone(str(work_position))

        work_position = WorkerPosition(
            data={"PositionStartDate": "1994-10-01T00:00:00.000Z",
                  "PositionEndDate": str(datetime.now(timezone.utc) +
                                         timedelta(minutes=1)),
                  "IsFutureDate": False,
                  "PositionFTEPercent": "100.00000"})
        self.assertTrue(work_position.is_active_position())
        self.assertFalse(work_position.is_future_date)

        work_position = WorkerPosition(
            data={"PositionStartDate": str(datetime.now(timezone.utc) +
                                           timedelta(minutes=1)),
                  "IsFutureDate": True,
                  "PositionEndDate": None,
                  "PositionFTEPercent": "100.00000"})
        self.assertTrue(work_position.is_future_date)
        self.assertTrue(work_position.is_active_position())

        work_position = WorkerPosition(
            data={"PositionStartDate": None,
                  "IsFutureDate": False,
                  "PositionEndDate": None,
                  "PositionFTEPercent": "0.00000"})
        self.assertIsNotNone(work_position)

    def test_worker(self):
        worker = Worker(netid='none',
                        regid="10000000",
                        employee_id="100000115")
        self.assertIsNotNone(str(worker))
        data = {
            "NetID": "webmaster",
            "RegID": "10000000000000000000000000000115",
            "EmployeeID": "100000115",
            "WorkerEmploymentStatus": {
                "ActiveStatusDate": "1980-07-01T07:00:00.000Z",
                "EmployeeStatus": "Active",
                "EmployeeStatusCode": "A",
                "EndEmploymentDate": None,
                "EstimatedLastDayOfLeave": None,
                "FirstDayOfLeave": None,
                "FirstDayOfWork": "1980-07-01T07:00:00.000Z",
                "HireDate": "1980-07-01T07:00:00.000Z",
                "IsActive": True,
                "IsRetired": False,
                "IsTerminated": False,
                "LastDayOfWorkForLeave": None,
                "OriginalHireDate": "1980-07-01T07:00:00.000Z",
                "RetirementDate": None,
                "TerminationDate": None},
            "WorkerPositions": [{
                "PositionBusinessTitle": "Web Support Specialist",
                "PositionSupervisor": {
                    "EmployeeID": "000000005",
                    "Href": "/hrp/v2/worker/000000005.json"},
                "PositionTimeTypeID": "Full_time",
                "PositionTitle": "COM SUP ANA 2, Web and Social Media",
                "SupervisoryOrganization": {
                    "AcademicUnitID": None,
                    "Code": "UWB: ",
                    "ID": "UWB_000066",
                    "Name": "Web and Social Media",
                    "Description": "UWB: Web and Social Media ()",
                    "Href": "/hrp/v2/organization/UWB_000066.json",
                    "CostCenter": {
                        "Description": "ADV & EXT RELATIONS -B",
                        "ID": "060304",
                        "OrganizationCode": "5014010000",
                        "OrganizationDescription": "BR-B OFFICE OF ADV"}},
                "PositionID": "PN-0036224",
                "PositionEffectiveDate": "2015-12-21T08:00:00.000Z",
                "IsPrimaryPosition": True,
                "PositionStartDate": "2015-12-21T00:00:00.000Z",
                "PositionEndDate": None,
                "PositionType": "Regular",
                "PositionFTEPercent": "100.00000",
                "PayRateType": "Salary",
                "TotalBasePayFrequency": "Monthly",
                "WorkShift": "First Shift",
                "ServicePeriodID": "12",
                "ServicePeriodDescription": "Service_Period_12.00",
                "JobProfileSummary": {},
                "CostCenter": {
                    "Description": "ADV & EXT RELATIONS -B",
                    "ID": "060304",
                    "OrganizationCode": "5014010000",
                    "OrganizationDescription": "BR-B OFFICE OF ADV"},
                "EcsJobClassificationCode": "B",
                "EcsJobClassificationCodeDescription": "Classified Staff",
                "ObjectCode": "01",
                "SubObjectCode": "60",
                "PayrollUnitCode": "00356",
                "IsOnLeaveFromPosition": False,
                "IsFutureDate": False,
                "IsMedicalCenterPosition": False,
                "Location": {"ID": "Bothell Campus",
                             "Name": "Bothell Campus"},
                "FutureTransactions": []},
                {"CostCenter": {
                    "Description": "INFORMATION SCHOOL",
                    "ID": "061630",
                    "OrganizationCode": "2670001000",
                    "OrganizationDescription": "THE INFORMATION SCHOOL"},
                 "EcsJobClassificationCode": "U",
                 "EcsJobClassificationCodeDescription": "Undergrad Student",
                 "FutureTransactions": [],
                 "IsFutureDate": False,
                 "IsMedicalCenterPosition": False,
                 "IsOnLeaveFromPosition": False,
                 "IsPrimaryPosition": False,
                 "JobProfileSummary": {
                     "Href": "/hrp/v2/jobProfile/10886.json",
                     "JobCategory": "Hourly and Other",
                     "JobFamilies": [],
                     "JobProfileDescription": "Reader/Grader (NE H UAW ASE)",
                     "JobProfileID": "10886"},
                 "Location": {"ID": "Seattle Campus",
                              "Name": "Seattle Campus"},
                 "ObjectCode": "01",
                 "PayRateType": "Hourly",
                 "PayrollUnitCode": "00652",
                 "PlannedDistributions": {
                     "PeriodActivityAssignments": [],
                     "PlannedCompensationAllocations": [],
                 },
                 "PositionBusinessTitle": "Reader/Grader",
                 "PositionEffectiveDate": "2017-09-16T07:00:00.000Z",
                 "PositionEndDate": None,
                 "PositionFTEPercent": "10.00000",
                 "PositionID": "PN-0086428",
                 "PositionStartDate": "2017-09-16T00:00:00.000Z",
                 "PositionSupervisor": {
                     "EmployeeID": "000004000",
                     "Href": "/hrp/v2/worker/000004000.json"},
                 "PositionTimeTypeID": "Part_time",
                 "PositionTitle": "Reader/Grader",
                 "PositionType": "Temporary",
                 "ServicePeriodDescription": "Service_Period_12.00",
                 "ServicePeriodID": "12",
                 "SubObjectCode": "80",
                 "SupervisoryOrganization": None,
                 "WorkShift": "First Shift"}],
            "AcademicAppointments": [],
            "SystemMetadata": {"LastModified": None}}
        worker = Worker(data=data)
        self.assertEqual(worker.netid, 'webmaster')
        self.assertEqual(worker.employee_id, '100000115')
        self.assertEqual(worker.primary_manager_id, '000000005')
        self.assertEqual(
            worker.primary_position.to_json(),
            {'ecs_job_cla_code_desc': 'Classified Staff',
             'end_date': None,
             'fte_percent': 100.0,
             'is_future_date': False,
             'is_primary': True,
             'job_profile': {'description': None, 'job_code': None},
             'location': 'Bothell Campus',
             'payroll_unit_code': '00356',
             'pos_time_type_id': 'Full_time',
             'pos_type': 'Regular',
             'start_date': '2015-12-21 00:00:00+00:00',
             'supervisor_eid': '000000005',
             'supervisory_org': {
                 'budget_code': '5014010000',
                 'org_code': 'UWB:',
                 'org_name': 'Web and Social Media'},
             'title': 'Web Support Specialist'})
        self.assertIsNotNone(str(worker.primary_position))
        self.assertEqual(len(worker.other_active_positions), 1)
        self.assertIsNotNone(str(worker.employee_status))
        self.assertIsNotNone(str(worker))

        data = {
            "NetID": "webmaster",
            "RegID": "10000000000000000000000000000115",
            "EmployeeID": "100000115",
            "WorkerEmploymentStatus": {
                "IsActive": False,
                "EmployeeStatus": "Terminated",
                "EmployeeStatusCode": "N",
                "IsTerminated": True,
                "EndEmploymentDate": None,
                "HireDate": "1980-07-01T07:00:00.000Z",
                "IsRetired": False,
                "RetirementDate": None,
                "TerminationDate": None},
            "WorkerPositions": []}
        worker = Worker(data=data)
        self.assertIsNone(worker.primary_position)
        self.assertEqual(len(worker.other_active_positions), 0)
        self.assertTrue(worker.employee_status.is_terminated)
        self.assertFalse(worker.employee_status.is_active)
        self.assertIsNotNone(str(worker))
