from django.contrib import admin

from apps.compensation.models import CompensationBand


@admin.register(CompensationBand)
class CompensationBandAdmin(admin.ModelAdmin):
    list_display = ["role", "level", "location", "company_size", "p50", "sample_size"]
    list_filter = ["company_size", "level", "location"]
    search_fields = ["role", "location"]
    ordering = ["role", "level"]
