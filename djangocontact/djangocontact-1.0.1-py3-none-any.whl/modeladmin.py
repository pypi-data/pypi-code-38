from django.contrib import admin


# Register ModelAdmin here.
class EmailModelAdmin(admin.ModelAdmin):
    list_display  = ['full_name', 'from_email']
    list_filter   = ['created_at', 'updated_at']
    search_fields = ['full_name', 'to_email', 'phone_number']
    list_per_page = 10
    
    fieldsets = (
        ("Subscriber", {
            "classes" : ["extrapretty"],
            "fields" : ["full_name"],
        }),
        ("Personal information", {
            "classes" : ["collapse", "extrapretty"],
            "fields" : ["to_email", "phone_number"],
        }),
        ("Message", {
            "classes" : ["collapse", "extrapretty"],
            "fields" : ["subject", "content"],
        }),
    )
