from edc_form_validators import FormValidator
from edc_constants.constants import YES, UNKNOWN


class AeInitialFormValidator(FormValidator):
    def clean(self):

        drugs = [
            "fluconazole_relation",
            "flucytosine_relation",
            "amphotericin_relation",
        ]
        for drug in drugs:
            self.applicable_if(
                YES,
                UNKNOWN,
                field="ae_study_relation_possibility",
                field_applicable=drug,
            )

        self.validate_other_specify(field="ae_classification")

        self.required_if(YES, field="ae_cause", field_required="ae_cause_other")

        self.applicable_if(YES, field="sae", field_applicable="sae_reason")

        self.applicable_if(YES, field="susar", field_applicable="susar_reported")
