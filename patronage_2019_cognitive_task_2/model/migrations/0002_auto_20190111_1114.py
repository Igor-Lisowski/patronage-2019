# Generated by Django 2.1.5 on 2019-01-11 11:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='person',
            old_name='salary',
            new_name='salary_brutto',
        ),
    ]
