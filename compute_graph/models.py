from django.db import models
from django.conf import settings
# Create your models here.

class StatList(models.Model):
    name = models.CharField(max_length=200)
    script = models.FilePathField(path=settings.FILE_PATH_FIELD_DIRECTORY)
    family_name = models.CharField(max_length=200)
    params_list = models.FilePathField(path=settings.FILE_PATH_FIELD_DIRECTORY,default=settings.FILE_PATH_FIELD_DIRECTORY)

