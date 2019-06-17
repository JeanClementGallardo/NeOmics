import re
import socket
import subprocess
import uuid

from django.db import models

from ImportRaw.models import Project
from NeOmics import settings

non_alpha_pattern = re.compile(r'\W')


def simplify(string):
    string = string.replace(' ', '_')
    return re.sub(non_alpha_pattern, '', string)


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

    def execute(self, **parameters):
        subprocess.call(
            [settings.BASE_DIR + "/NeOmics/R-3.6.0/bin/Rscript", self.script.path] +
            ["--{}={}".format(param, parameters[param]) for param in parameters])


class Graph(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    analysis_family = models.ForeignKey(AnalysisFamily, on_delete=models.CASCADE)
    http_port = models.IntegerField(default=7474)
    bolt_port = models.IntegerField(default=7687)
    name = models.CharField(default="graph", max_length=500)
    uri = models.CharField(default="bolt://localhost:7687", max_length=200)
    user = models.CharField(default="neo4j", max_length=200)
    password = models.CharField(default="neo4j", max_length=200)

    @classmethod
    def create(cls, current_host: str, project, analysis_family):
        current_host = current_host
        address = ':'.join(current_host.split(':')[:-1])

        try:
            graph = Graph.objects.get(project=project, analysis_family=analysis_family)
        except Graph.DoesNotExist:

            # Get new free port
            s1 = socket.socket()
            s2 = socket.socket()
            s1.bind((address, 0))
            s2.bind((address, 0))
            http_port = s1.getsockname()[1]
            bolt_port = s2.getsockname()[1]
            s1.close()
            s2.close()

            db_name = "{}_analysis_results_on_{}".format(simplify(analysis_family.name), simplify(project.name))

            uri = "bolt://{}:{}".format(address, bolt_port)
            user = uuid.uuid4().hex
            password = uuid.uuid4().hex

            root_path = settings.BASE_DIR + '/NeOmics'

            subprocess.call([root_path + '/neo4j-installer.sh',
                             root_path,
                             db_name,
                             address,
                             str(bolt_port),
                             str(http_port),
                             user,
                             password])

            launcher = '{}/neo4j_instances/{}/bin/neo4j'.format(root_path, db_name)

            graph = cls(project=project, analysis_family=analysis_family, name=db_name, uri=uri, user=user,
                        password=password, http_port=http_port, bolt_port=bolt_port)
            graph.save()
            return graph
        else:
            return graph

    @property
    def launcher(self):
        return '{}/NeOmics/neo4j_instances/{}/bin/neo4j'.format(settings.BASE_DIR, self.name)

    def start(self):
        subprocess.call([self.launcher, "start"])

    def stop(self):
        subprocess.call([self.launcher, "stop"])

    def __str__(self):
        return "{}_analysis_results_on_{}".format(simplify(self.analysis_family.name), simplify(self.project.name))

    def delete(self, using=None, keep_parents=False):
        super(Graph, self).delete()
        subprocess.call(["rm", '-rf', '/'.join(self.launcher.split('/')[:-2])])
