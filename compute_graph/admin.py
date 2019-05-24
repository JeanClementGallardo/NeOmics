from django.contrib import admin

from .models import Analysis, AnalysisFamily

# Register your models here.
admin.site.register(AnalysisFamily)
admin.site.register(Analysis)
