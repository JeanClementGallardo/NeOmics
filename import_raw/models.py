from django.db import models


# Create your models here.
class Labkey(models.Model):
    uri = models.CharField(max_length=200)
    users = models.CharField(max_length=200)
    password = models.CharField(max_length=200)


class Path(models.Model):
    filepath = models.FilePathField(max_length=500)


