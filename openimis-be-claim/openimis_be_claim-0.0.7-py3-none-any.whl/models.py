from django.db import models
from core import fields
from core import models as core_models
from location import models as location_models
from insuree import models as insuree_models
from medical import models as medical_models
from policy import models as policy_models


class ClaimAdmin(models.Model):
    id = models.AutoField(db_column='ClaimAdminId', primary_key=True)
    legacy_id = models.IntegerField(
        db_column='LegacyId', blank=True, null=True)
    code = models.CharField(db_column='ClaimAdminCode',
                            max_length=8, blank=True, null=True)
    last_name = models.CharField(
        db_column='LastName', max_length=100, blank=True, null=True)
    other_names = models.CharField(
        db_column='OtherNames', max_length=100, blank=True, null=True)
    dob = models.DateField(db_column='DOB', blank=True, null=True)
    email_id = models.CharField(
        db_column='EmailId', max_length=200, blank=True, null=True)
    phone = models.CharField(
        db_column='Phone', max_length=50, blank=True, null=True)
    health_facility = models.ForeignKey(
        location_models.HealthFacility, models.DO_NOTHING, db_column='HFId', blank=True, null=True)
    validity_from = fields.DateTimeField(
        db_column='ValidityFrom', blank=True, null=True)
    validity_to = fields.DateTimeField(
        db_column='ValidityTo', blank=True, null=True)    
    has_login = models.BooleanField(db_column='HasLogin', blank=True, null=True)

    audit_user_id = models.IntegerField(
        db_column='AuditUserId', blank=True, null=True)
    # row_id = models.BinaryField(db_column='RowId', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblClaimAdmin'


class ClaimDiagnosisCode(models.Model):
    id = models.AutoField(db_column='ICDID', primary_key=True)
    legacy_id = models.IntegerField(
        db_column='LegacyID', blank=True, null=True)
    code = models.CharField(db_column='ICDCode', max_length=6)
    name = models.CharField(db_column='ICDName', max_length=255)
    validity_from = fields.DateTimeField(db_column='ValidityFrom')
    validity_to = fields.DateTimeField(
        db_column='ValidityTo', blank=True, null=True)

    audit_user_id = models.IntegerField(db_column='AuditUserID')
    # row_id = models.BinaryField(db_column='RowID', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblICDCodes'


class Feedback(models.Model):
    id = models.AutoField(db_column='FeedbackID', primary_key=True)
    legacy_id = models.IntegerField(
        db_column='LegacyID', blank=True, null=True)
    care_rendered = models.BooleanField(
        db_column='CareRendered', blank=True, null=True)
    payment_asked = models.BooleanField(
        db_column='PaymentAsked', blank=True, null=True)
    drug_prescribed = models.BooleanField(
        db_column='DrugPrescribed', blank=True, null=True)
    drug_received = models.BooleanField(
        db_column='DrugReceived', blank=True, null=True)
    asessment = models.SmallIntegerField(
        db_column='Asessment', blank=True, null=True)
    chf_officer_code = models.IntegerField(
        db_column='CHFOfficerCode', blank=True, null=True)
    feedback_date = fields.DateTimeField(
        db_column='FeedbackDate', blank=True, null=True)
    validity_from = fields.DateTimeField(db_column='ValidityFrom')
    validity_to = fields.DateTimeField(
        db_column='ValidityTo', blank=True, null=True)
    audit_user_id = models.IntegerField(db_column='AuditUserID')

    class Meta:
        managed = False
        db_table = 'tblFeedback'


class Claim(models.Model):
    id = models.AutoField(db_column='ClaimID', primary_key=True)
    legacy_id = models.IntegerField(
        db_column='LegacyID', blank=True, null=True)
    category = models.CharField(
        db_column='ClaimCategory', max_length=1, blank=True, null=True)
    insuree = models.ForeignKey(
        insuree_models.Insuree, models.DO_NOTHING, db_column='InsureeID')
    code = models.CharField(db_column='ClaimCode', max_length=8)
    date_from = fields.DateField(db_column='DateFrom')
    date_to = fields.DateField(db_column='DateTo', blank=True, null=True)
    status = models.SmallIntegerField(db_column='ClaimStatus')
    adjuster = models.ForeignKey(
        core_models.InteractiveUser, models.DO_NOTHING, db_column='Adjuster', blank=True, null=True)
    adjustment = models.TextField(
        db_column='Adjustment', blank=True, null=True)
    claimed = models.DecimalField(
        db_column='Claimed', max_digits=18, decimal_places=2, blank=True, null=True)
    approved = models.DecimalField(
        db_column='Approved', max_digits=18, decimal_places=2, blank=True, null=True)
    reinsured = models.DecimalField(
        db_column='Reinsured', max_digits=18, decimal_places=2, blank=True, null=True)
    valuated = models.DecimalField(
        db_column='Valuated', max_digits=18, decimal_places=2, blank=True, null=True)
    date_claimed = fields.DateField(db_column='DateClaimed')
    date_processed = fields.DateField(
        db_column='DateProcessed', blank=True, null=True)
    feedback = models.BooleanField(db_column='Feedback')
    feedback = models.OneToOneField(
        Feedback, models.DO_NOTHING, db_column='FeedbackID', blank=True, null=True)
    explanation = models.TextField(
        db_column='Explanation', blank=True, null=True)
    feedback_status = models.SmallIntegerField(
        db_column='FeedbackStatus', blank=True, null=True)
    review_status = models.SmallIntegerField(
        db_column='ReviewStatus', blank=True, null=True)
    approval_status = models.SmallIntegerField(
        db_column='ApprovalStatus', blank=True, null=True)
    rejection_reason = models.SmallIntegerField(
        db_column='RejectionReason', blank=True, null=True)

    validity_from = fields.DateTimeField(db_column='ValidityFrom')
    validity_to = fields.DateTimeField(
        db_column='ValidityTo', blank=True, null=True)

    audit_user_id = models.IntegerField(db_column='AuditUserID')
    validity_from_review = fields.DateTimeField(
        db_column='ValidityFromReview', blank=True, null=True)
    validity_to_review = fields.DateTimeField(
        db_column='ValidityToReview', blank=True, null=True)

    health_facility = models.ForeignKey(
        location_models.HealthFacility, models.DO_NOTHING, db_column='HFID')
    # runid = models.ForeignKey(Tblbatchrun, models.DO_NOTHING, db_column='RunID', blank=True, null=True)

    submit_stamp = fields.DateTimeField(
        db_column='SubmitStamp', blank=True, null=True)
    process_stamp = fields.DateTimeField(
        db_column='ProcessStamp', blank=True, null=True)
    remunerated = models.DecimalField(
        db_column='Remunerated', max_digits=18, decimal_places=2, blank=True, null=True)
    guarantee_id = models.CharField(
        db_column='GuaranteeId', max_length=50, blank=True, null=True)
    admin = models.ForeignKey(
        ClaimAdmin, models.DO_NOTHING, db_column='ClaimAdminId', blank=True, null=True)
    icd = models.ForeignKey(
        ClaimDiagnosisCode, models.DO_NOTHING, db_column='ICDID')
    icd_1 = models.IntegerField(db_column='ICDID1', blank=True, null=True)
    icd_2 = models.IntegerField(db_column='ICDID2', blank=True, null=True)
    icd_3 = models.IntegerField(db_column='ICDID3', blank=True, null=True)
    icd_4 = models.IntegerField(db_column='ICDID4', blank=True, null=True)

    visit_type = models.CharField(
        db_column='VisitType', max_length=1, blank=True, null=True)
    audit_user_id_review = models.IntegerField(
        db_column='AuditUserIDReview', blank=True, null=True)
    audit_user_id_submit = models.IntegerField(
        db_column='AuditUserIDSubmit', blank=True, null=True)
    audit_user_id_process = models.IntegerField(
        db_column='AuditUserIDProcess', blank=True, null=True)
    # row_id = models.BinaryField(db_column='RowID', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblClaim'


class ClaimItem(models.Model):
    id = models.AutoField(db_column='ClaimItemID', primary_key=True)
    legacy_id = models.IntegerField(
        db_column='LegacyID', blank=True, null=True)
    claim = models.ForeignKey(Claim, models.DO_NOTHING, db_column='ClaimID')
    item = models.ForeignKey(
        medical_models.Item, models.DO_NOTHING, db_column='ItemID')
    # prodid = models.ForeignKey('Tblproduct', models.DO_NOTHING, db_column='ProdID', blank=True, null=True)
    status = models.SmallIntegerField(db_column='ClaimItemStatus')
    availability = models.BooleanField(db_column='Availability')
    qty_provided = models.DecimalField(
        db_column='QtyProvided', max_digits=18, decimal_places=2)
    qty_approved = models.DecimalField(
        db_column='QtyApproved', max_digits=18, decimal_places=2, blank=True, null=True)
    price_asked = models.DecimalField(
        db_column='PriceAsked', max_digits=18, decimal_places=2)
    price_adjusted = models.DecimalField(
        db_column='PriceAdjusted', max_digits=18, decimal_places=2, blank=True, null=True)
    price_approved = models.DecimalField(
        db_column='PriceApproved', max_digits=18, decimal_places=2, blank=True, null=True)
    price_valuated = models.DecimalField(
        db_column='PriceValuated', max_digits=18, decimal_places=2, blank=True, null=True)
    explanation = models.TextField(
        db_column='Explanation', blank=True, null=True)
    justification = models.TextField(
        db_column='Justification', blank=True, null=True)
    rejection_reason = models.SmallIntegerField(
        db_column='RejectionReason', blank=True, null=True)
    validity_from = fields.DateTimeField(db_column='ValidityFrom')
    validity_to = fields.DateTimeField(
        db_column='ValidityTo', blank=True, null=True)
    audit_user_id = models.IntegerField(db_column='AuditUserID')
    validity_from_review = fields.DateTimeField(
        db_column='ValidityFromReview', blank=True, null=True)
    validity_to_review = fields.DateTimeField(
        db_column='ValidityToReview', blank=True, null=True)
    audit_user_id_review = models.IntegerField(
        db_column='AuditUserIDReview', blank=True, null=True)
    limitation_value = models.DecimalField(
        db_column='LimitationValue', max_digits=18, decimal_places=2, blank=True, null=True)
    limitation = models.CharField(
        db_column='Limitation', max_length=1, blank=True, null=True)
    policy = models.ForeignKey(
        policy_models.Policy, models.DO_NOTHING, db_column='PolicyID', blank=True, null=True)
    remunerated_amount = models.DecimalField(
        db_column='RemuneratedAmount', max_digits=18, decimal_places=2, blank=True, null=True)
    deductable_amount = models.DecimalField(
        db_column='DeductableAmount', max_digits=18, decimal_places=2, blank=True, null=True)
    exceed_ceiling_amount = models.DecimalField(
        db_column='ExceedCeilingAmount', max_digits=18, decimal_places=2, blank=True, null=True)
    price_origin = models.CharField(
        db_column='PriceOrigin', max_length=1, blank=True, null=True)
    exceed_ceiling_amount_category = models.DecimalField(
        db_column='ExceedCeilingAmountCategory', max_digits=18, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblClaimItems'


class ClaimService(models.Model):
    id = models.AutoField(db_column='ClaimServiceID', primary_key=True)
    legacy_id = models.IntegerField(
        db_column='LegacyID', blank=True, null=True)
    claim = models.ForeignKey(
        Claim, models.DO_NOTHING, db_column='ClaimID')
    service = models.ForeignKey(
        medical_models.Service, models.DO_NOTHING, db_column='ServiceID')
    # prod = models.ForeignKey('Tblproduct', models.DO_NOTHING, db_column='ProdID', blank=True, null=True)
    status = models.SmallIntegerField(db_column='ClaimServiceStatus')
    qty_provided = models.DecimalField(
        db_column='QtyProvided', max_digits=18, decimal_places=2)
    qty_approved = models.DecimalField(
        db_column='QtyApproved', max_digits=18, decimal_places=2, blank=True, null=True)
    price_asked = models.DecimalField(
        db_column='PriceAsked', max_digits=18, decimal_places=2)
    price_adjusted = models.DecimalField(
        db_column='PriceAdjusted', max_digits=18, decimal_places=2, blank=True, null=True)
    price_approved = models.DecimalField(
        db_column='PriceApproved', max_digits=18, decimal_places=2, blank=True, null=True)
    price_valuated = models.DecimalField(
        db_column='PriceValuated', max_digits=18, decimal_places=2, blank=True, null=True)
    explanation = models.TextField(
        db_column='Explanation', blank=True, null=True)
    justification = models.TextField(
        db_column='Justification', blank=True, null=True)
    rejectionreason = models.SmallIntegerField(
        db_column='RejectionReason', blank=True, null=True)
    validity_from = fields.DateTimeField(db_column='ValidityFrom')
    validity_to = fields.DateTimeField(
        db_column='ValidityTo', blank=True, null=True)
    audit_user_id = models.IntegerField(db_column='AuditUserID')
    validity_from_review = fields.DateTimeField(
        db_column='ValidityFromReview', blank=True, null=True)
    validity_to_review = fields.DateTimeField(
        db_column='ValidityToReview', blank=True, null=True)
    audit_user_id_review = models.IntegerField(
        db_column='AuditUserIDReview', blank=True, null=True)
    limitation_value = models.DecimalField(
        db_column='LimitationValue', max_digits=18, decimal_places=2, blank=True, null=True)
    limitation = models.CharField(
        db_column='Limitation', max_length=1, blank=True, null=True)
    policy = models.ForeignKey(
        policy_models.Policy, models.DO_NOTHING, db_column='PolicyID', blank=True, null=True)
    remunerated_amount = models.DecimalField(
        db_column='RemuneratedAmount', max_digits=18, decimal_places=2, blank=True, null=True)
    deductable_amount = models.DecimalField(
        db_column='DeductableAmount', max_digits=18, decimal_places=2, blank=True, null=True)
    exceed_ceiling_amount = models.DecimalField(
        db_column='ExceedCeilingAmount', max_digits=18, decimal_places=2, blank=True, null=True)
    price_origin = models.CharField(
        db_column='PriceOrigin', max_length=1, blank=True, null=True)
    exceed_ceiling_amount_category = models.DecimalField(
        db_column='ExceedCeilingAmountCategory', max_digits=18, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblClaimServices'
