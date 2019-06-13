# Generated by Django 2.2 on 2019-06-12 14:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ImportRaw', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnalysisFamily',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Graph',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('http_port', models.IntegerField(default=7474)),
                ('bolt_port', models.IntegerField(default=7687)),
                ('name', models.CharField(default='graph', max_length=500)),
                ('uri', models.CharField(default='bolt://localhost:7687', max_length=200)),
                ('user', models.CharField(default='neo4j', max_length=200)),
                ('password', models.CharField(default='neo4j', max_length=200)),
                ('analysis_family', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ComputeGraph.AnalysisFamily')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ImportRaw.Project')),
            ],
        ),
        migrations.CreateModel(
            name='Analysis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('script', models.FileField(upload_to='Scripts')),
                ('parameters_json_file', models.FileField(upload_to='Scripts/Params')),
                ('family', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ComputeGraph.AnalysisFamily')),
            ],
        ),
    ]
