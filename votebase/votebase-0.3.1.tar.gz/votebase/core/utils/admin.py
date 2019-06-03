from votebase.core.utils.common import duplicate


def duplicate_object(modeladmin, request, queryset):
    # sd is an instance of SemesterDetails
    for o in queryset:
        duplicate(o)
