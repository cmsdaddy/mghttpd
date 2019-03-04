# Generated by Django 2.0.5 on 2018-06-05 10:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ui', '0012_historyrecord_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collector',
            name='datapoints',
        ),
        migrations.RemoveField(
            model_name='collector',
            name='disabled',
        ),
        migrations.RemoveField(
            model_name='collector',
            name='host',
        ),
        migrations.RemoveField(
            model_name='collector',
            name='name',
        ),
        migrations.RemoveField(
            model_name='collector',
            name='period',
        ),
        migrations.RemoveField(
            model_name='collector',
            name='protocol',
        ),
        migrations.RemoveField(
            model_name='datapointrecords',
            name='datapoint',
        ),
        migrations.AddField(
            model_name='collector',
            name='path',
            field=models.TextField(default='invalid', help_text='数据点路径'),
        ),
        migrations.AddField(
            model_name='datapointrecords',
            name='collector',
            field=models.ForeignKey(help_text='记录的数据点ID', null=True, on_delete=django.db.models.deletion.CASCADE, to='ui.Collector'),
        ),
    ]
