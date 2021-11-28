# Generated by Django 3.1.3 on 2021-11-28 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0021_auto_20211122_0923'),
    ]

    operations = [
        migrations.AddField(
            model_name='basel_collateral_master',
            name='account_no_temp',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='basel_product_master',
            name='account_no_temp',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='db_mange',
            name='table_name',
            field=models.CharField(blank=True, choices=[('Master', 'Master'), ('user', 'User'), ('PD Initial', 'PD Initial'), ('LGD Initial', 'LGD Initial'), ('Stage Initial', 'Stage Initial'), ('EIR Initial', 'EIR Initial'), ('ECL Initial', 'ECL Initial'), ('EAD Initial', 'EAD Initial'), ('PD Final', 'PD Final'), ('LGD Final', 'LGD Final'), ('Stage Final', 'Stage Final'), ('EIR Final', 'EIR Final'), ('ECL Final', 'ECL Final'), ('EAD Final', 'EAD Final'), ('PD Report', 'PD Report'), ('LGD Final', 'LGD Report'), ('Stage Report', 'Stage Report'), ('EIR Report', 'EIR Report'), ('ECL Report', 'ECL Report'), ('EAD Report', 'EAD Report')], db_index=True, max_length=255, null=True),
        ),
    ]
