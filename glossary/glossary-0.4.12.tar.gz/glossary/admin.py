from django.contrib import admin

from mptt.admin import MPTTModelAdmin

from glossary import models


class GlossaryAdmin(admin.ModelAdmin):
    exclude = ("uuid", "deleted", )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.Faculty)
class FacultyAdmin(GlossaryAdmin):
    readonly_fields = ("name", )


@admin.register(models.Department)
class DepartmentAdmin(GlossaryAdmin):
    readonly_fields = ("name", "faculty")


@admin.register(models.AcademicGroup)
class AcademicGroupAdmin(GlossaryAdmin):
    readonly_fields = ("name", "faculty", "year")
    list_filter = ("faculty", )
    list_display = ("name", "faculty", "year")


@admin.register(models.Address)
class AddressAdmin(GlossaryAdmin):
    pass


@admin.register(models.Campus)
class CampusAdmin(GlossaryAdmin):
    pass


@admin.register(models.RoomType)
class RoomTypeAdmin(GlossaryAdmin):
    pass


@admin.register(models.Room)
class RoomAdmin(GlossaryAdmin):
    pass


@admin.register(models.Subdivision)
class SubdivisionAdmin(MPTTModelAdmin, GlossaryAdmin):
    pass