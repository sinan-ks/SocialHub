# Generated by Django 5.0.1 on 2024-03-14 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='name',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
