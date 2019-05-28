from django.db import models
from ImportRaw.models import RawData


# Create your models here.
class AnalysisFamily(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Analysis(models.Model):
    name = models.CharField(max_length=200)
    script = models.FileField(upload_to='Scripts')
    family = models.ForeignKey(AnalysisFamily, on_delete=models.CASCADE)
    parameters_json_file = models.FileField(upload_to='Scripts/Params')

    def __str__(self):
        return self.name


class Graph(models.Model):
    organism = models.ForeignKey(RawData, on_delete=models.CASCADE)
    analysis_family = models.ForeignKey(AnalysisFamily, on_delete=models.CASCADE)
    neo4j_uri = models.CharField(default="bolt://localhost:7687", max_length=200)
    neo4j_user = models.CharField(default="neo4j", max_length=200)
    neo4j_password = models.CharField(default="neo4j", max_length=200)

    def __str__(self):
        return "{} analysis results on {}".format(self.analysis_family.name, self.organism.organism)
