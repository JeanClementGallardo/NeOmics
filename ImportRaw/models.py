from django.db import models


# # Create your models here.
# class Labkey(models.Model):
#     uri = models.CharField(max_length=200)
#     users = models.CharField(max_length=200)
#     password = models.CharField(max_length=200)


class RawData(models.Model):
    organism = models.CharField(max_length=200)
    labkey_url = models.URLField()

    def __str__(self):
        return self.organism

