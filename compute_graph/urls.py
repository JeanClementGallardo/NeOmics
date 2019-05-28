from django.urls import path

from . import views

app_name = "compute_graph"
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<organism>', views.StatView.as_view(), name='stat_choice'),
    path('<organism>/<name>', views.stat_params, name='stat_params'),
    path('<organism>/<name>/stat_load', views.stat_load, name='stat_load'),
]
