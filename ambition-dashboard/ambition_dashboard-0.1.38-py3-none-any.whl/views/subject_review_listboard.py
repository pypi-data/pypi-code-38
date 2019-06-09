from django.conf import settings
from edc_review_dashboard.views import SubjectReviewListboardView as Base
from edc_subject_model_wrappers import SubjectVisitModelWrapper


class SubjectReviewListboardView(Base):

    listboard_model = settings.SUBJECT_VISIT_MODEL
    model_wrapper_cls = SubjectVisitModelWrapper
    navbar_name = "ambition_dashboard"
