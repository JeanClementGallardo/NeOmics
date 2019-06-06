from django.urls import path

from . import views

app_name = "Viewer"
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<graph>', views.graph, name="graph"),
]
