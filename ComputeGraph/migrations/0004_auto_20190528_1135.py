# Generated by Django 2.2 on 2019-05-28 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ComputeGraph', '0003_auto_20190524_1606'),
    ]

    operations = [
        migrations.AlterField(
            model_name='graph',
            name='neo4j_uri',
            field=models.CharField(default='bolt://localhost:7687', max_length=200),
        ),
    ]
