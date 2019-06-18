from django.db import models
from core import fields


class Policy(models.Model):
    id = models.AutoField(db_column='PolicyID', primary_key=True)
    legacy_id = models.IntegerField(
        db_column='LegacyID', blank=True, null=True)

    stage = models.CharField(db_column='PolicyStage',
                             max_length=1, blank=True, null=True)
    status = models.SmallIntegerField(
        db_column='PolicyStatus', blank=True, null=True)
    value = models.DecimalField(
        db_column='PolicyValue', max_digits=18, decimal_places=2, blank=True, null=True)

    # familyid = models.ForeignKey(Tblfamilies, models.DO_NOTHING, db_column='FamilyID')
    enroll_date = fields.DateField(db_column='EnrollDate')
    start_date = fields.DateField(db_column='StartDate')
    effective_date = fields.DateField(
        db_column='EffectiveDate', blank=True, null=True)
    expiry_date = fields.DateField(
        db_column='ExpiryDate', blank=True, null=True)

    # prodid = models.ForeignKey('Tblproduct', models.DO_NOTHING, db_column='ProdID')
    # officerid = models.ForeignKey(Tblofficer, models.DO_NOTHING, db_column='OfficerID', blank=True, null=True)

    validity_from = fields.DateTimeField(db_column='ValidityFrom')
    validity_to = fields.DateTimeField(
        db_column='ValidityTo', blank=True, null=True)

    offline = models.BooleanField(db_column='isOffline', blank=True, null=True)
    audit_user_id = models.IntegerField(db_column='AuditUserID')
    # row_id = models.BinaryField(db_column='RowID', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblPolicy'
