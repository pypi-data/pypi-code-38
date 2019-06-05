from edc_notification import GradedEventNotification
from edc_notification import register


@register()
class AeInitialG3EventNotification(GradedEventNotification):

    name = "g3_aeinitial"
    display_name = "a grade 3 initial event has occurred"
    grade = 3
    model = "ambition_ae.aeinitial"


@register()
class AeFollowupG3EventNotification(GradedEventNotification):

    name = "g3_aefollowup"
    display_name = "a grade 3 followup event has occurred"
    grade = 3
    model = "ambition_ae.aefollowup"


@register()
class AeInitialG4EventNotification(GradedEventNotification):

    name = "g4_aeinitial"
    display_name = "a grade 4 initial event has occurred"
    grade = 4
    model = "ambition_ae.aeinitial"


@register()
class AeFollowupG4EventNotification(GradedEventNotification):

    name = "g4_aefollowup"
    display_name = "a grade 4 followup event has occurred"
    grade = 4
    model = "ambition_ae.aefollowup"
