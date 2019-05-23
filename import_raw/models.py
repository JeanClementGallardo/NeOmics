from django.db import models


# Create your models here.

class Labkey(models.Model):
    URI_text = models.CharField(max_length=500)
    user = models.CharField(max_length=100)
    password = models.CharField(max_length=100)


class Path(models.Model):
    filepath = models.FilePathField(max_length=500)
