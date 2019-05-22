from django.db import models


# Create your models here.
class Graph(models.Model):
    uri = models.CharField(max_length=200)
