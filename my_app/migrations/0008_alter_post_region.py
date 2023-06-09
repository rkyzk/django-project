# Generated by Django 3.2.18 on 2023-04-02 03:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0007_alter_comment_comment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='region',
            field=models.CharField(choices=[('N/A', 'N/A'), ('NAM', 'North America'), ('CAM', 'Central America'), ('CRB', 'Caribbean'), ('SAM', 'South America'), ('NEU', 'Northern Europe'), ('WEU', 'Western Europe'), ('EEU', 'Eastern Europe'), ('SEU', 'Southern Europe'), ('NAF', 'North Africa'), ('WAF', 'Western Africa'), ('MAF', 'Middle Africa'), ('EAF', 'Eastern Africa'), ('SAF', 'Southern Africa'), ('SAF', 'Southern Africa'), ('WAS', 'Western Asia'), ('CAS', 'Central Asia'), ('EAS', 'Eastern Asia'), ('SAS', 'Southern Asia'), ('SAS', 'Southeastern Asia'), ('ANZ', 'Australia and New Zealand'), ('PIS', 'Pacific Islands')], default='N/A', max_length=30),
        ),
    ]
