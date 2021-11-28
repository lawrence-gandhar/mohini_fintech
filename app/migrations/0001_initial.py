# Generated by Django 3.1.3 on 2021-09-16 19:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountMaster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('cin', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('account_no', models.BigIntegerField(db_index=True, unique=True)),
                ('account_type', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('product_name', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('sectors', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('customer_name', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('contact_no', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('email', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('pan', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('aadhar_no', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('customer_addr', models.TextField(blank=True, null=True)),
                ('pin', models.IntegerField(blank=True, db_index=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PD_Report',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('factor_1', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('factor_2', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('factor_3', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('factor_4', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('factor_5', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('factor_6', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('default_col', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('mgmt_overlay_1', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('mgmt_overlay_2', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('intercept', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('coeff_fact1', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('coeff_fact2', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('coeff_fact3', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('coeff_fact4', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('pd', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('account_no', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.accountmaster')),
            ],
        ),
        migrations.CreateModel(
            name='PD_Intial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('factor_1', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('factor_2', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('factor_3', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('factor_4', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('factor_5', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('factor_6', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('default_col', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('mgmt_overlay_1', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('mgmt_overlay_2', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('file_identifier', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('edited_on', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('account_no', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.accountmaster')),
                ('edited_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PD_Final',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('factor_1', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('factor_2', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('factor_3', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('factor_4', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('factor_5', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('factor_6', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('default_col', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('mgmt_overlay_1', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('mgmt_overlay_2', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('file_identifier', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('account_no', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.accountmaster')),
            ],
        ),
    ]
