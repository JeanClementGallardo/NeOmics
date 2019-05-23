from django.urls import path

from . import views

app_name = "compute_graph"
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<organism>',views.stat_choice, name='stat_choice'),
]