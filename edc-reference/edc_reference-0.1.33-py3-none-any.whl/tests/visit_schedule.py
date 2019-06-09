from dateutil.relativedelta import relativedelta
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.visit import FormsCollection, Crf, Visit
from edc_visit_schedule.visit_schedule import VisitSchedule


crfs = FormsCollection(Crf(show_order=1, model=f"edc_reference.crfone", required=True))


visit0 = Visit(
    code="1000",
    title="Day 1",
    timepoint=0,
    rbase=relativedelta(days=0),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    crfs=crfs,
    facility_name="default",
)

schedule = Schedule(
    name="schedule",
    onschedule_model="edc_reference.onschedule",
    offschedule_model="edc_reference.offschedule",
    appointment_model="edc_appointment.appointment",
    consent_model="edc_reference.subjectconsent",
)

schedule.add_visit(visit0)

visit_schedule = VisitSchedule(
    name="visit_schedule",
    offstudy_model="edc_reference.subjectoffstudy",
    death_report_model="edc_reference.deathreport",
)

visit_schedule.add_schedule(schedule)
