# Generated by Django 3.2.6 on 2021-08-28 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_student'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='description',
            field=models.TextField(max_length=500),
        ),
    ]
