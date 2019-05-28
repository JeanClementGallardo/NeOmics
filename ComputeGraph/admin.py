from django.contrib import admin

from .models import Analysis, AnalysisFamily, Graph

# Register your models here.
admin.site.register(AnalysisFamily)
admin.site.register(Analysis)
admin.site.register(Graph)