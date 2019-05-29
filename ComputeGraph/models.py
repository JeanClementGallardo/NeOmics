from django.db import models
from ImportRaw.models import RawData
import socket


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
    neo4j_password = models.CharField(default="admin", max_length=200)

    def __str__(self):
        return "{} analysis results on {}".format(self.analysis_family.name, self.organism.organism)


class GraphManager(models.Manager):
    def __init__(self, host: str):
        self.host = host
        self.address = ':'.join(host.split(':')[:-1])
        super().__init__()

    def create_graph(self, organism, analysis_family) -> Graph:
        """Generate new graph if it doesn't already exist, and gives it otherwise"""
        try:
            graph = Graph.objects.get(organism=organism, analysis_family=analysis_family)
        except Graph.DoesNotExist:
            # Get new free port
            sock = socket.socket()
            sock.bind(('', 0))
            new_port = sock.getsockname()[1]
            sock.close()

            new_uri = self.address + new_port

            # TODO Generate new instance of neo4j
            # See http://fooo.fr/~vjeux/github/github-recommandation/db/doc/manual/html/server-installation.html

            return self.create(organism=organism, analysis_family=analysis_family, neo4j_uri=new_uri)
        else:
            return graph
