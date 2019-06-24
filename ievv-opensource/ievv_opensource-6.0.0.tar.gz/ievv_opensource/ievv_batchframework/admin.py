from django.contrib import admin

from ievv_opensource.ievv_batchframework.models import BatchOperation


@admin.register(BatchOperation)
class BatchOperationAdmin(admin.ModelAdmin):
    list_per_page = 20

    list_display = [
        'id',
        'status',
        'operationtype',
        'started_by',
        'created_datetime',
        'started_running_datetime',
        'finished_datetime',
        'context_object',
    ]

    readonly_fields = [
        'input_data_json',
        'output_data_json',
        'result',
        'status',
    ]

    list_filter = [
        'status',
        'created_datetime',
        'started_running_datetime',
        'finished_datetime',
    ]
