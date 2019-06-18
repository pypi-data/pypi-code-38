from django.test import TestCase
from django.core.exceptions import PermissionDenied
from unittest import mock
import xml.etree.ElementTree as ET
from .services import *
import core


class ClaimSubmitServiceTestCase(TestCase):

    def test_minimal_item_claim_submit_xml(self):
        items = [
            ClaimItemSubmit(code='aa', quantity=2),
        ]
        item = "<Item><ItemCode>aa</ItemCode><ItemQuantity>2</ItemQuantity></Item>"

        claim = ClaimSubmit(
            date=core.datetime.date(2020, 1, 9),
            code="code_ABVC",
            icd_code="ICD_CODE_WWQ",
            total=334,
            start_date=core.datetime.date(2020, 1, 13),
            claim_admin_code='ADM_CODE_ADKJ',
            insuree_chf_id='CHFID_UUZIS',
            health_facility_code="HFCode_JQL",
            item_submits=items,
        )
        details = "<Details>"
        details = details + "<ClaimDate>09/01/2020</ClaimDate>"
        details = details + "<HFCode>HFCode_JQL</HFCode>"
        details = details + "<ClaimAdmin>ADM_CODE_ADKJ</ClaimAdmin>"
        details = details + "<ClaimCode>code_ABVC</ClaimCode>"
        details = details + "<CHFID>CHFID_UUZIS</CHFID>"
        details = details + "<StartDate>13/01/2020</StartDate>"
        details = details + "<ICDCode>ICD_CODE_WWQ</ICDCode>"
        details = details + "<Total>334</Total>"
        details = details + "</Details>"
        expected = "<Claim>%s<Items>%s</Items></Claim>" % (details, item)
        self.assertEquals(expected, claim.to_xml())

    def test_minimal_service_claim_submit_xml(self):
        services = [
            ClaimServiceSubmit(code='aa', quantity=2),
        ]
        service = "<Service><ServiceCode>aa</ServiceCode><ServiceQuantity>2</ServiceQuantity></Service>"

        claim = ClaimSubmit(
            date=core.datetime.date(2020, 1, 9),
            code="code_ABVC",
            icd_code="ICD_CODE_WWQ",
            total=334,
            start_date=core.datetime.date(2020, 1, 13),
            claim_admin_code='ADM_CODE_ADKJ',
            insuree_chf_id='CHFID_UUZIS',
            health_facility_code="HFCode_JQL",
            service_submits=services,
        )
        details = "<Details>"
        details = details + "<ClaimDate>09/01/2020</ClaimDate>"
        details = details + "<HFCode>HFCode_JQL</HFCode>"
        details = details + "<ClaimAdmin>ADM_CODE_ADKJ</ClaimAdmin>"
        details = details + "<ClaimCode>code_ABVC</ClaimCode>"
        details = details + "<CHFID>CHFID_UUZIS</CHFID>"
        details = details + "<StartDate>13/01/2020</StartDate>"
        details = details + "<ICDCode>ICD_CODE_WWQ</ICDCode>"
        details = details + "<Total>334</Total>"
        details = details + "</Details>"
        expected = "<Claim>%s<Services>%s</Services></Claim>" % (
            details, service)
        self.assertEquals(expected, claim.to_xml())

    def test_extended_claim_submit_xml(self):
        items = [
            ClaimItemSubmit(code='aa', quantity=2),
            ClaimItemSubmit(code='bb', quantity=1, price=12.3),
        ]
        item_a = "<Item><ItemCode>aa</ItemCode><ItemQuantity>2</ItemQuantity></Item>"
        item_b = "<Item><ItemCode>bb</ItemCode><ItemPrice>12.3</ItemPrice><ItemQuantity>1</ItemQuantity></Item>"

        services = [
            ClaimServiceSubmit(code='aa-serv', quantity=2),
            ClaimServiceSubmit(code='a<a\'-serv', quantity=1, price=35),
        ]
        service_a = "<Service><ServiceCode>aa-serv</ServiceCode><ServiceQuantity>2</ServiceQuantity></Service>"
        service_b = "<Service><ServiceCode>a&lt;a\'-serv</ServiceCode><ServicePrice>35</ServicePrice><ServiceQuantity>1</ServiceQuantity></Service>"

        claim = ClaimSubmit(
            date=core.datetime.date(2020, 1, 9),
            code="code_ABVC",
            icd_code="ICD_CODE_WWQ",
            total=334,
            start_date=core.datetime.date(2020, 1, 13),
            claim_admin_code='ADM_CODE_ADKJ',
            insuree_chf_id='CHFID_UUZIS',
            health_facility_code="HFCode_JQL",
            item_submits=items,
            service_submits=services
        )
        details = "<Details>"
        details = details + "<ClaimDate>09/01/2020</ClaimDate>"
        details = details + "<HFCode>HFCode_JQL</HFCode>"
        details = details + "<ClaimAdmin>ADM_CODE_ADKJ</ClaimAdmin>"
        details = details + "<ClaimCode>code_ABVC</ClaimCode>"
        details = details + "<CHFID>CHFID_UUZIS</CHFID>"
        details = details + "<StartDate>13/01/2020</StartDate>"
        details = details + "<ICDCode>ICD_CODE_WWQ</ICDCode>"
        details = details + "<Total>334</Total>"
        details = details + "</Details>"
        expected = "<Claim>%s" % details
        expected = expected + "<Items>%s%s</Items>" % (item_a, item_b)
        expected = expected + \
            "<Services>%s%s</Services>" % (service_a, service_b)
        expected = expected + "</Claim>"
        self.assertEquals(expected, claim.to_xml())

    def test_claim_submit_permission_denied(self):
        with mock.patch("django.db.backends.utils.CursorWrapper") as mock_cursor:
            mock_cursor.return_value.__enter__.return_value.fetchone.return_value = [
                2]
            mock_user = mock.Mock(is_anonymous=False)
            mock_user.has_perm = mock.MagicMock(return_value=False)
            claim = ClaimSubmit(
                date=core.datetime.date(2020, 1, 9),
                code="code_ABVC",
                icd_code="ICD_CODE_WWQ",
                total=334,
                start_date=core.datetime.date(2020, 1, 13),
                claim_admin_code='ADM_CODE_ADKJ',
                insuree_chf_id='CHFID_UUZIS',
                health_facility_code="HFCode_JQL"
            )
            service = ClaimSubmitService(user=mock_user)
            with self.assertRaises(PermissionDenied) as cm:
                service.submit(claim)

    def test_claim_submit_error(self):
        with mock.patch("django.db.backends.utils.CursorWrapper") as mock_cursor:
            mock_cursor.return_value.__enter__.return_value.fetchone.return_value = [
                2]
            mock_user = mock.Mock(is_anonymous=False)
            mock_user.has_perm = mock.MagicMock(return_value=True)
            claim = ClaimSubmit(
                date=core.datetime.date(2020, 1, 9),
                code="code_ABVC",
                icd_code="ICD_CODE_WWQ",
                total=334,
                start_date=core.datetime.date(2020, 1, 13),
                claim_admin_code='ADM_CODE_ADKJ',
                insuree_chf_id='CHFID_UUZIS',
                health_facility_code="HFCode_JQL"
            )
            service = ClaimSubmitService(user=mock_user)
            with self.assertRaises(ClaimSubmitError) as cm:
                service.submit(claim)
            self.assertEquals(cm.exception.code, 2)
            mock_user.has_perm.assert_called_with('claim.can_add')

    def test_claim_submit_allgood(self):
        with mock.patch("django.db.backends.utils.CursorWrapper") as mock_cursor:
            mock_cursor.return_value.__enter__.return_value.description = None
            mock_user = mock.Mock(is_anonymous=False)
            mock_user.has_perm = mock.MagicMock(return_value=True)
            claim = ClaimSubmit(
                date=core.datetime.date(2020, 1, 9),
                code="code_ABVC",
                icd_code="ICD_CODE_WWQ",
                total=334,
                start_date=core.datetime.date(2020, 1, 13),
                claim_admin_code='ADM_CODE_ADKJ',
                insuree_chf_id='CHFID_UUZIS',
                health_facility_code="HFCode_JQL"
            )
            service = ClaimSubmitService(user=mock_user)
            service.submit(claim)  # doesn't raise an error
            mock_user.has_perm.assert_called_with('claim.can_add')


class EligibilityServiceTestCase(TestCase):

    def test_eligibility_request_permission_denied(self):
        with mock.patch("django.db.backends.utils.CursorWrapper") as mock_cursor:
            mock_cursor.return_value.__enter__.return_value.description = None
            mock_user = mock.Mock(is_anonymous=False)
            mock_user.has_perm = mock.MagicMock(return_value=False)
            req = EligibilityRequest(chfid='a')
            service = EligibilityService(mock_user)
            with self.assertRaises(PermissionDenied) as cm:
                service.request(req)
            mock_user.has_perm.assert_called_with('claim.can_view')

    def test_eligibility_request_all_good(self):
        with mock.patch("django.db.backends.utils.CursorWrapper") as mock_cursor:
            return_values = [
                list(range(1, 13)),
                [core.datetime.date(2020, 1, 9),
                 core.datetime.date(2020, 1, 10),
                 20, 21, True, True]
            ][::-1]

            mock_cursor.return_value.__enter__.return_value.fetchone = lambda: return_values.pop()
            mock_user = mock.Mock(is_anonymous=False)
            mock_user.has_perm = mock.MagicMock(return_value=True)
            req = EligibilityRequest(chfid='a')
            service = EligibilityService(mock_user)
            res = service.request(req)

            excpected = EligibilityResponse(
                eligibility_request=req,
                prod_id=1,
                total_admissions_left=2,
                total_visits_left=3,
                total_consultations_left=4,
                total_surgeries_left=5,
                total_delivieries_left=6,
                total_antenatal_left=7,
                consultation_amount_left=8,
                surgery_amount_left=9,
                delivery_amount_left=10,
                hospitalization_amount_left=11,
                antenatal_amount_left=12,
                min_date_service=core.datetime.date(2020, 1, 9),
                min_date_item=core.datetime.date(2020, 1, 10),
                service_left=20,
                item_left=21,
                is_item_ok=True,
                is_service_ok= True
            )
            self.assertEquals(excpected, res)
