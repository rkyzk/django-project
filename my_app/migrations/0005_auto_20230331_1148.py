# Generated by Django 3.2.18 on 2023-03-31 11:48

import cloudinary.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0004_comment_comment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='published_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='image',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, verbose_name='image'),
        ),
    ]
