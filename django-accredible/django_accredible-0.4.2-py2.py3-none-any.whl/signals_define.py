from django.dispatch import Signal


create_certification_group = Signal(
    use_caching=True)

update_certification_group = Signal(
    providing_args=['instance', 'user_from'],
    use_caching=True)

delete_certification_group = Signal(
    providing_args=['instance'],
    use_caching=True)

create_certification_credential = Signal(
    providing_args=[
        'certification_group', 'user_from', 'certification_credential'],
    use_caching=True)

create_certification_group_credential = Signal(
    providing_args=['user_from', 'course_name', 'issued_on'],
    use_caching=True)
