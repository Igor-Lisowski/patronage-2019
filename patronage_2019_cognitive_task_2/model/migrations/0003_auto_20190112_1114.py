# Generated by Django 2.1.5 on 2019-01-12 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0002_auto_20190111_1114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='salary_brutto',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
    ]