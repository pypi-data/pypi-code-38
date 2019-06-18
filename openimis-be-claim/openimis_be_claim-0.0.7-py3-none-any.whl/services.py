from django.db import connection
import xml.etree.ElementTree as ET
from django.core.exceptions import PermissionDenied
import core

@core.comparable
class ClaimElementSubmit(object):
    def __init__(self, type, code, quantity, price=None):
        self.type = type
        self.code = code
        self.price = price
        self.quantity = quantity

    def add_to_xmlelt(self, xmlelt):
        item = ET.SubElement(xmlelt, self.type)
        ET.SubElement(item, "%sCode" % self.type).text = "%s" % self.code
        if self.price:
            ET.SubElement(item, "%sPrice" % self.type).text = "%s" % self.price
        ET.SubElement(item, "%sQuantity" %
                      self.type).text = "%s" % self.quantity

@core.comparable
class ClaimItemSubmit(ClaimElementSubmit):
    def __init__(self, code, quantity, price=None):
        super().__init__(type='Item',
                         code=code,
                         price=price,
                         quantity=quantity)

@core.comparable
class ClaimServiceSubmit(ClaimElementSubmit):
    def __init__(self, code, quantity, price=None):
        super().__init__(type='Service',
                         code=code,
                         price=price,
                         quantity=quantity)
@core.comparable
class ClaimSubmit(object):
    def __init__(self, date, code, icd_code, total, start_date,
                 insuree_chf_id, health_facility_code,
                 claim_admin_code,
                 item_submits=None, service_submits=None,
                 end_date=None,
                 icd_code_1=None, icd_code_2=None, icd_code_3=None, icd_code_4=None,
                 visit_type=None, guarantee_no=None,
                 comment=None,
                 ):
        self.date = date
        self.code = code
        self.icd_code = icd_code
        self.total = total
        self.start_date = start_date
        self.insuree_chf_id = insuree_chf_id
        self.health_facility_code = health_facility_code
        self.end_date = end_date
        self.icd_code_1 = icd_code_1
        self.icd_code_2 = icd_code_2
        self.icd_code_3 = icd_code_3
        self.icd_code_4 = icd_code_4
        self.claim_admin_code = claim_admin_code
        self.visit_type = visit_type
        self.guarantee_no = guarantee_no
        self.comment = comment
        self.items = item_submits
        self.services = service_submits

    def _details_to_xmlelt(self, xmlelt):
        ET.SubElement(xmlelt, 'ClaimDate').text = self.date.to_ad_date().strftime(
            "%d/%m/%Y")
        ET.SubElement(
            xmlelt, 'HFCode').text = "%s" % self.health_facility_code
        if self.claim_admin_code:
            ET.SubElement(
                xmlelt, 'ClaimAdmin').text = "%s" % self.claim_admin_code
        ET.SubElement(xmlelt, 'ClaimCode').text = "%s" % self.code
        ET.SubElement(xmlelt, 'CHFID').text = "%s" % self.insuree_chf_id
        ET.SubElement(
            xmlelt, 'StartDate').text = self.start_date.to_ad_date().strftime("%d/%m/%Y")
        if self.end_date:
            ET.SubElement(xmlelt, 'EndDate').text = self.end_date.to_ad_date().strftime(
                "%d/%m/%Y")
        ET.SubElement(xmlelt, 'ICDCode').text = "%s" % self.icd_code
        if self.comment:
            ET.SubElement(xmlelt, 'Comment').text = "%s" % self.comment
        ET.SubElement(xmlelt, 'Total').text = "%s" % self.total
        if self.icd_code_1:
            ET.SubElement(xmlelt, 'ICDCode1').text = "%s" % self.icd_code_1
        if self.icd_code_2:
            ET.SubElement(xmlelt, 'ICDCode1').text = "%s" % self.icd_code_2
        if self.icd_code_3:
            ET.SubElement(xmlelt, 'ICDCode1').text = "%s" % self.icd_code_3
        if self.icd_code_4:
            ET.SubElement(xmlelt, 'ICDCode1').text = "%s" % self.icd_code_4
        if self.visit_type:
            ET.SubElement(xmlelt, 'VisitType').text = "%s" % self.visit_type
        if self.guarantee_no:
            ET.SubElement(
                xmlelt, 'GuaranteeNo').text = "%s" % self.guarantee_no
   
    def add_elt_list_to_xmlelt(self, xmlelt, elts_name, elts):
        if elts and len(elts) > 0:
            elts_xml = ET.SubElement(xmlelt, elts_name)
            for item in elts:
                item.add_to_xmlelt(elts_xml)

    def add_to_xmlelt(self, xmlelt):
        details = ET.SubElement(xmlelt, 'Details')
        self._details_to_xmlelt(details)
        self.add_elt_list_to_xmlelt(xmlelt, 'Items', self.items)
        self.add_elt_list_to_xmlelt(xmlelt, 'Services', self.services)

    def to_xml(self):
        claim_xml = ET.Element('Claim')
        self.add_to_xmlelt(claim_xml)
        return ET.tostring(claim_xml, encoding='utf-8', method='xml').decode()

@core.comparable
class ClaimSubmitError(Exception):
    ERROR_CODES = {
        -1: "Fatal Error",
        1: "Invalid HF Code",
        2: "Duplicate Claim Code",
        3: "Invalid Insuree CHFID",
        4: "End date is smaller than start date",
        5: "Invalid ICDCode",
        6: "Claimed amount is 0",
        7: "Invalid ItemCode",
        8: "Invalid ServiceCode",
        9: "Invalid Claim Admin",
    }

    def __init__(self, code, msg=None):
        self.code = code
        self.msg = ClaimSubmitError.ERROR_CODES.get(
            self.code, msg or "Unknown exception")

    def __str__(self):
        return "ClaimSubmitError %s: %s" % (self.code, self.msg)


class ClaimSubmitService(object):

    def __init__(self, user):
        self.user = user

    def submit(self, claim_submit):
        if self.user.is_anonymous or not self.user.has_perm('claim.can_add'):
            raise PermissionDenied
        with connection.cursor() as cur:
            sql = """\
                DECLARE @ret int;
                EXEC @ret = [dbo].[uspUpdateClaimFromPhone] @XML = %s;
                SELECT @ret;
            """

            cur.execute(sql, (claim_submit.to_xml(),))
            cur.nextset()  # skip 'DECLARE...' (non) result
            cur.nextset()  # skip 'EXEC...' (non) result
            if cur.description is None:  # 0 is considered as 'no result' by pyodbc
                return
            res = cur.fetchone()[0]  # FETCH 'SELECT @ret' returned value
            raise ClaimSubmitError(res)

@core.comparable
class EligibilityRequest(object):

    def __init__(self, chfid, service_code=None, item_code=None):
        self.chfid = chfid
        self.service_code = service_code
        self.item_code = item_code

    def __eq__(self, other):
        import pdb; pdb.set_trace()        
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__        

@core.comparable
class EligibilityResponse(object):

    def __init__(self, eligibility_request, prod_id, total_admissions_left, total_visits_left, total_consultations_left, total_surgeries_left,
                 total_delivieries_left, total_antenatal_left, consultation_amount_left, surgery_amount_left, delivery_amount_left,
                 hospitalization_amount_left, antenatal_amount_left,
                 min_date_service, min_date_item, service_left, item_left, is_item_ok, is_service_ok):
        self.eligibility_request = eligibility_request
        self.prod_id = prod_id
        self.total_admissions_left = total_admissions_left
        self.total_visits_left = total_visits_left
        self.total_consultations_left = total_consultations_left
        self.total_surgeries_left = total_surgeries_left
        self.total_delivieries_left = total_delivieries_left
        self.total_antenatal_left = total_antenatal_left
        self.consultation_amount_left = consultation_amount_left
        self.surgery_amount_left = surgery_amount_left
        self.delivery_amount_left = delivery_amount_left
        self.hospitalization_amount_left = hospitalization_amount_left
        self.antenatal_amount_left = antenatal_amount_left
        self.min_date_service = min_date_service
        self.min_date_item = min_date_item
        self.service_left = service_left
        self.item_left = item_left
        self.is_item_ok = is_item_ok
        self.is_service_ok = is_service_ok


class EligibilityService(object):

    def __init__(self, user):
        self.user = user

    def request(self, eligibility_request):
        if self.user.is_anonymous or not self.user.has_perm('claim.can_view'):
            raise PermissionDenied
        with connection.cursor() as cur:
            sql = """\
                DECLARE @MinDateService DATE, @MinDateItem DATE,
                        @ServiceLeft INT, @ItemLeft INT,
                        @isItemOK BIT, @isServiceOK BIT;
                EXEC [dbo].[uspServiceItemEnquiry] @CHFID = %s, @ServiceCode = %s, @ItemCode = %s,
                     @MinDateService = @MinDateService, @MinDateItem = @MinDateItem,
                     @ServiceLeft = @ServiceLeft, @ItemLeft = @ItemLeft,
                     @isItemOK = @isItemOK, @isServiceOK = @isServiceOK;
                SELECT @MinDateService, @MinDateItem, @ServiceLeft, @ItemLeft, @isItemOK, @isServiceOK
            """
            cur.execute(sql, (eligibility_request.chfid,
                              eligibility_request.service_code,
                              eligibility_request.item_code))
            (prod_id, total_admissions_left, total_visits_left, total_consultations_left, total_surgeries_left,
             total_delivieries_left, total_antenatal_left, consultation_amount_left, surgery_amount_left, delivery_amount_left,
             hospitalization_amount_left, antenatal_amount_left) = cur.fetchone()  # retrieve the stored proc @Result table
            cur.nextset()
            (min_date_service, min_date_item, service_left,
             item_left, is_item_ok, is_service_ok) = cur.fetchone()
            return EligibilityResponse(
                eligibility_request=eligibility_request,
                prod_id=prod_id or None,
                total_admissions_left=total_admissions_left or 0,
                total_visits_left=total_visits_left or 0,
                total_consultations_left=total_consultations_left or 0,
                total_surgeries_left=total_surgeries_left or 0,
                total_delivieries_left=total_delivieries_left or 0,
                total_antenatal_left=total_antenatal_left or 0,
                consultation_amount_left=consultation_amount_left or 0.0,
                surgery_amount_left=surgery_amount_left or 0.0,
                delivery_amount_left=delivery_amount_left or 0.0,
                hospitalization_amount_left=hospitalization_amount_left or 0.0,
                antenatal_amount_left=antenatal_amount_left or 0.0,
                min_date_service=core.datetime.date.from_ad_date(
                    min_date_service),
                min_date_item=core.datetime.date.from_ad_date(min_date_item),
                service_left=service_left or 0,
                item_left=item_left or 0,
                is_item_ok=is_item_ok == True,
                is_service_ok=is_service_ok == True
            )