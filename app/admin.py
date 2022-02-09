from django.contrib import admin
from . models import *
# Register your models here.

#******************************************************************************
#
#******************************************************************************

admin.site.site_header = 'Finecl'
admin.site.site_title = "Finecl"


@admin.register(PD_Report)
class PD_ReportAdmin(admin.ModelAdmin):
    model = PD_Report
    list_display = [field.name for field in PD_Report._meta.get_fields() if field.name !="ecl_missing_reports"]

@admin.register(LGD_Report)
class LGD_ReportAdmin(admin.ModelAdmin):
    model = LGD_Report
    list_display = [field.name for field in LGD_Report._meta.get_fields() if field.name !="ecl_missing_reports"]

@admin.register(Stage_Report)
class Stage_ReportAdmin(admin.ModelAdmin):
    model = Stage_Report
    list_display = [field.name for field in Stage_Report._meta.get_fields() if field.name !="ecl_missing_reports"]

@admin.register(EAD_Report)
class EAD_ReportAdmin(admin.ModelAdmin):
    model = EAD_Report
    list_display = [field.name for field in EAD_Report._meta.get_fields() if field.name !="ecl_missing_reports"]

@admin.register(ECL_Reports)
class ECL_ReportsAdmin(admin.ModelAdmin):
    model = ECL_Reports
    list_display = [field.name for field in ECL_Reports._meta.get_fields() if field.name !="ecl_missing_reports"]

@admin.register(ECL_Missing_Reports)
class ECL_Missing_ReportsAdmin(admin.ModelAdmin):
    model = ECL_Missing_Reports
    list_display = [field.name for field in ECL_Missing_Reports._meta.get_fields() if field.name !="ecl_missing_reports"]
