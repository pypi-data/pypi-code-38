from django.contrib import admin

from invoices.models import Invoice, InvoiceLine


class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'recipient', 'total', 'date', 'status')
    list_filter = ('status',)
    search_fields = ('reference_number', 'recipient__username',
                     'recipient__first_name', 'recipient__last_name')
    inlines = [InvoiceLineInline]


admin.site.register(Invoice, InvoiceAdmin)
