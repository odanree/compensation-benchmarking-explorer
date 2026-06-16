from django.contrib import admin

from apps.solar.models import CostBand


@admin.register(CostBand)
class CostBandAdmin(admin.ModelAdmin):
    list_display = [
        "system_size_range", "panel_tier", "location", "installer_type",
        "p50", "sample_size",
    ]
    list_filter = ["installer_type", "panel_tier", "location"]
    search_fields = ["location", "system_size_range"]
    ordering = ["location", "system_size_range", "panel_tier"]
