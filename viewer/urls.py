from django.urls import path

from . import views

app_name = "viewer"
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<organism>',views.graph, name="graph"),
]
