from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import connection

#==================================================================================
# NEW USER SIGNUP DETAILS
#==================================================================================

class New_User(models.Model):
    email = models.EmailField(blank=False, null=False, max_length=250, db_index=True,)
    first_name = models.TextField(blank=False, null=False, max_length=250, db_index=True)
    last_name = models.TextField(blank=False, null=False, max_length=250, db_index=True)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True)
    email_sent_on = models.DateTimeField(auto_now_add=False, db_index=True, blank=True, null=True)
    status = models.IntegerField(default=0, db_index=True, null=True, blank=True)

#==================================================================================
# NEW USER SIGNUP DETAILS
#==================================================================================

class AccessManage(models.Model):
    user = models.ForeignKey(User, db_index=True, null=True, blank=True, on_delete=models.CASCADE, related_name="accessmanage_user")
    upload_master_table = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    edit_master_table = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    delete_master_table = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    upload_basel_product = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    edit_basel_product = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    delete_basel_product = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    upload_basel_collateral = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    edit_basel_collateral = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    delete_basel_collateral = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    upload_collateral_mapper = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    edit_collateral_mapper = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    delete_collateral_mapper = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    upload_pd = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    upload_lgd = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    upload_ead = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    upload_ecl = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    upload_eir = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    upload_stage = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    edit_import_pd = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    edit_import_lgd = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    edit_import_ead = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    edit_import_ecl = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    edit_import_eir = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    edit_import_stage = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    delete_import_pd = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    delete_import_lgd = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    delete_import_ead = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    delete_import_ecl = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    delete_import_eir = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    delete_import_stage = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    edit_final_pd = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    edit_final_lgd = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    edit_final_ead = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    edit_final_ecl = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    edit_final_eir = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    edit_final_stage = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    delete_final_pd = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    delete_final_lgd = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    delete_final_ead = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    delete_final_ecl = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    delete_final_eir = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    delete_final_stage = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    run_final_pd = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    run_final_lgd = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    run_final_ead = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    run_final_ecl = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    run_final_eir = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    run_final_stage = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    download_reports_pd = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    download_reports_lgd = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    download_reports_ead = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    download_reports_ecl = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    download_reports_eir = models.IntegerField(default=0, db_index=True, null=True, blank=True)
    download_reports_stage = models.IntegerField(default=0, db_index=True, null=True, blank=True)


#==================================================================================
# ACCOUNT MASTER
#==================================================================================
class AccountMaster(models.Model):
    cin = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    account_no = models.CharField(blank=False, null=False, max_length=255, db_index=True, unique=True)
    account_type = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    account_status = models.BooleanField(default=True, null=True, db_index=True)
    sectors = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    customer_name = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    contact_no = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    email = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    pan = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    aadhar_no = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    customer_addr = models.TextField(blank=True, null=True,)
    pin = models.IntegerField(blank=True, null=True, db_index=True)
    file_identifier = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return self.account_no

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" SET_NULL'.format(cls._meta.db_table))


#==================================================================================
# ACCOUNT MASTER
#==================================================================================
class AccountMissing(models.Model):
    account_no = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    file_identifier = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True)



#==================================================================================
# PD INITIAL
#==================================================================================
class PD_Initial(models.Model):
    date = models.DateField(auto_now_add=False, null=True, blank=True,)
    account_no = models.ForeignKey(AccountMaster, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    account_no_temp = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    factor_1 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    factor_2 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    factor_3 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    factor_4 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    factor_5 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    factor_6 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    default_col = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    mgmt_overlay_1 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    mgmt_overlay_2 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    file_identifier = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    created_on = models.DateTimeField(auto_now=True, db_index=True)
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    edited_on = models.DateTimeField(db_index=True, null=True, blank=True)

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" SET_NULL'.format(cls._meta.db_table))

#==================================================================================
# PD FINAL
#==================================================================================
class PD_Final(models.Model):
    date = models.DateField(auto_now_add=False, null=True, blank=True,)
    account_no = models.ForeignKey(AccountMaster, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    factor_1 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    factor_2 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    factor_3 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    factor_4 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    factor_5 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    factor_6 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    default_col = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    mgmt_overlay_1 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    mgmt_overlay_2 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    file_identifier = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True)

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" SET_NULL'.format(cls._meta.db_table))

#==================================================================================
# PD REPORT
#==================================================================================
class PD_Report(models.Model):
    date = models.DateField(auto_now_add=False, null=True, blank=True,)
    account_no = models.ForeignKey(AccountMaster, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    factor_1 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    factor_2 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    factor_3 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    factor_4 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    factor_5 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    factor_6 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    default_col = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    mgmt_overlay_1 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    mgmt_overlay_2 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    intercept = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    coeff_fact1 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    coeff_fact2 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    coeff_fact3 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    coeff_fact4 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    zscore = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    pd = models.CharField(blank=True, null=True, max_length=255, db_index=True)

    def __str__(self):
        return "[{}] - [{}]".format(self.date,self.account_no.account_no)

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" SET_NULL'.format(cls._meta.db_table))

#==================================================================================
# LGD INPUT - INITIAL TABLE
#==================================================================================
class LGD_Initial(models.Model):
    date = models.DateField(auto_now_add=False, null=True, blank=True,)
    account_no = models.ForeignKey(AccountMaster, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    account_no_temp = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    ead_os = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    pv_cashflows = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    pv_cost = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    beta_value = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    sec_flag = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    factor_4 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    factor_5 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    avg_1 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    avg_2 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    avg_3 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    avg_4 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    avg_5 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    mgmt_overlay_1 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    mgmt_overlay_2 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    file_identifier = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    created_on = models.DateTimeField(auto_now=True, db_index=True)
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    edited_on = models.DateTimeField(db_index=True, null=True, blank=True)

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" SET_NULL'.format(cls._meta.db_table))

#==================================================================================
# LGD FINAL
#==================================================================================
class LGD_Final(models.Model):
    date = models.DateField(auto_now_add=False, null=True, blank=True,)
    account_no = models.ForeignKey(AccountMaster, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    ead_os = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    pv_cashflows = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    pv_cost = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    beta_value = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    sec_flag = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    factor_4 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    factor_5 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    avg_1 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    avg_2 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    avg_3 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    avg_4 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    avg_5 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    mgmt_overlay_1 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    mgmt_overlay_2 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    file_identifier = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True)

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" SET_NULL'.format(cls._meta.db_table))

#==================================================================================
# LGD REPORT
#==================================================================================
class LGD_Report(models.Model):
    date = models.DateField(auto_now_add=False, null=True, blank=True,)
    account_no = models.ForeignKey(AccountMaster, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    ead_os = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    pv_cashflows = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    pv_cost = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    beta_value = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    sec_flag = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    factor_4 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    factor_5 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    avg_1 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    avg_2 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    avg_3 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    avg_4 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    avg_5 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    mgmt_overlay_1 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    mgmt_overlay_2 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    rec_rate = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    est_rr = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    est_lgd = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    final_lgd = models.CharField(blank=True, null=True, max_length=255, db_index=True)

    def __str__(self):
        return "[{}] - [{}]".format(self.date,self.account_no.account_no)

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" SET_NULL'.format(cls._meta.db_table))

#==================================================================================
# STAGE INITIAL TABLE
#==================================================================================
class Stage_Initial(models.Model):
    date = models.DateField(auto_now_add=False, null=True, blank=True,)
    account_no = models.ForeignKey(AccountMaster, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    account_no_temp = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    old_rating = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    new_rating = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    rating_3 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    rating_4 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    rating_5 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    rating_6 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    rating_7 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_1 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_2 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_3 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_4 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_5 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_6 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_7 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_8 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_9 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_10 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_11 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_12 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_13 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_14 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_15 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    criteria = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    cooling_period_1 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    cooling_period_2 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    cooling_period_3 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    cooling_period_4 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    cooling_period_5 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    rbi_window = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    mgmt_overlay_1 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    mgmt_overlay_2 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    file_identifier = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    created_on = models.DateTimeField(auto_now=True, db_index=True)
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    edited_on = models.DateTimeField(db_index=True, null=True, blank=True)

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" SET_NULL'.format(cls._meta.db_table))

#==================================================================================
# STAGE FINAL TABLE
#==================================================================================
class Stage_Final(models.Model):
    date = models.DateField(auto_now_add=False, null=True, blank=True,)
    account_no = models.ForeignKey(AccountMaster, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    old_rating = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    new_rating = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    rating_3 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    rating_4 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    rating_5 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    rating_6 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    rating_7 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_1 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_2 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_3 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_4 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_5 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_6 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_7 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_8 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_9 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_10 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_11 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_12 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_13 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_14 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_15 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    criteria = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    cooling_period_1 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    cooling_period_2 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    cooling_period_3 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    cooling_period_4 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    cooling_period_5 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    rbi_window = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    mgmt_overlay_1 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    mgmt_overlay_2 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    edited_on = models.DateTimeField(db_index=True, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True, null=True, blank=True)

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" SET_NULL'.format(cls._meta.db_table))

#==================================================================================
# STAGE REPORT TABLE
#==================================================================================
class Stage_Report(models.Model):
    date = models.DateField(auto_now_add=False, null=True, blank=True,)
    account_no = models.ForeignKey(AccountMaster, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    state = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    stage = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    old_rating = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    new_rating = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    rating_3 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    rating_4 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    rating_5 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    rating_6 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    rating_7 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_1 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_2 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_3 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_4 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_5 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_6 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_7 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_8 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_9 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_10 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_11 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_12 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_13 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_14 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    day_bucket_15 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    criteria = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    cooling_period_1 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    cooling_period_2 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    cooling_period_3 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    cooling_period_4 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    cooling_period_5 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    rbi_window = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    mgmt_overlay_1 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    mgmt_overlay_2 = models.CharField(blank=True, null=True, max_length=255, db_index=True)

    def __str__(self):
        return "[{}] - [{}]".format(self.date,self.account_no.account_no)

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" SET_NULL'.format(cls._meta.db_table))

#==================================================================================
# EIR INITIAL TABLE
#==================================================================================
class EIR_Initial(models.Model):
    date = models.DateField(auto_now_add=False, null=True, blank=True,)
    account_no = models.ForeignKey(AccountMaster, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    account_no_temp = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    period = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    loan_availed = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    cost_avail = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    rate = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    emi = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    os_principal = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    os_interest = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    fair_value = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    coupon = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    discount_factor = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    col_1 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    col_2 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    col_3 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    default_eir = models.CharField(blank=True, null=True, max_length=10, db_index=True)
    cop_tagged = models.BooleanField(blank=True, null=True, default=False, db_index=True)
    file_identifier = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    created_on = models.DateTimeField(auto_now=True, db_index=True)
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    edited_on = models.DateTimeField(db_index=True, null=True, blank=True)

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" SET_NULL'.format(cls._meta.db_table))
            
#==================================================================================
# EIR INITIAL TABLE :: Only Raw Data
#==================================================================================
class EIR_Initial_RawData(models.Model):
    date = models.DateField(auto_now_add=False, null=True, blank=True,)
    account_no = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    period = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    loan_availed = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    cost_avail = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    rate = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    emi = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    os_principal = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    os_interest = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    fair_value = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    coupon = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    discount_factor = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    col_1 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    col_2 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    col_3 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    default_eir = models.CharField(blank=True, null=True, max_length=10, db_index=True)
    cop_tagged = models.BooleanField(blank=True, null=True, default=False, db_index=True)
    file_identifier = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    created_on = models.DateTimeField(auto_now=True, db_index=True)

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" SET_NULL'.format(cls._meta.db_table))

#==================================================================================
# EIR FINAL TABLE
#==================================================================================
class EIR_Final(models.Model):
    date = models.DateField(auto_now_add=False, null=True, blank=True,)
    account_no = models.ForeignKey(AccountMaster, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    period = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    loan_availed = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    cost_avail = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    rate = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    emi = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    os_principal = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    os_interest = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    fair_value = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    coupon = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    discount_factor = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    col_1 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    col_2 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    col_3 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    default_eir = models.CharField(blank=True, null=True, max_length=10, db_index=True)
    cop_tagged = models.BooleanField(blank=True, null=True, default=True, db_index=True)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True)

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" SET_NULL'.format(cls._meta.db_table))


#==================================================================================
# EIR REPORTS TABLE
#==================================================================================
class EIR_Reports(models.Model):
    date = models.DateField(auto_now_add=False, null=True, blank=True,)
    account_no = models.ForeignKey(AccountMaster, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    period = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    loan_availed = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    cost_avail = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    rate = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    emi = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    os_principal = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    os_interest = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    fair_value = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    coupon = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    discount_factor = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    col_1 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    col_2 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    col_3 = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    default_eir = models.CharField(blank=True, null=True, max_length=10, db_index=True)
    cop_tagged = models.BooleanField(blank=True, null=True, default=True, db_index=True)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True)

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" SET_NULL'.format(cls._meta.db_table))


#==================================================================================
# DB MANAGE TABLE
#==================================================================================
class DB_Mange(models.Model):

    table_choices = (
        ('Master', 'Master'),
        ('user', 'User'),
        ('PD Initial', 'PD Initial'),
        ('LGD Initial', 'LGD Initial'),
        ('Stage Initial', 'Stage Initial'),
        ('EIR Initial', 'EIR Initial'),
        ('ECL Initial', 'ECL Initial'),
        ('EAD Initial', 'EAD Initial'),
        ('PD Final', 'PD Final'),
        ('LGD Final', 'LGD Final'),
        ('Stage Final', 'Stage Final'),
        ('EIR Final', 'EIR Final'),
        ('ECL Final', 'ECL Final'),
        ('EAD Final', 'EAD Final'),
        ('PD Report', 'PD Report'),
        ('LGD Final', 'LGD Report'),
        ('Stage Report', 'Stage Report'),
        ('EIR Report', 'EIR Report'),
        ('ECL Report', 'ECL Report'),
        ('EAD Report', 'EAD Report'),
    )

    table_name = models.CharField(max_length=255, db_index=True, null=True, blank=True, choices=table_choices)
    process_name = models.CharField(max_length=1, db_index=True, null=True, blank=True, choices=(('F', 'Full'), ('R', 'Range')))
    start_date = models.DateTimeField(auto_now_add=True, db_index=True, null=True, blank=True)
    end_date = models.DateTimeField(db_index=True, null=True, blank=True)
    start_range_date = models.DateField(db_index=True, null=True, blank=True)
    end_range_date = models.DateField(db_index=True, null=True, blank=True)
    total_deleted = models.IntegerField(db_index=True, null=True, blank=True, default=0)
    executed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)



#==================================================================================
# PRODUCT MASTER
#==================================================================================
class Basel_Product_Master(models.Model):
    product_name = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    product_code = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    product_catgory = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    basel_product = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    basel_product_code = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    drawn_cff = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    cff_upto_1_yr = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    cff_gt_1_yr = models.CharField(blank=True, null=True, max_length=255, db_index=True)


#==================================================================================
# BASEL COLLATERAL
#==================================================================================
class Basel_Collateral_Master(models.Model):
    collateral_code = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    collateral_type = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    issuer_type = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    collateral_eligibity = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    rating_available = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    collateral_rating = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    residual_maturity = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    basel_collateral_type = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    basel_collateral_subtype = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    basel_collateral_code = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    basel_collateral_rating = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    soverign_issuer = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    other_issuer = models.CharField(blank=True, null=True, max_length=255, db_index=True)


#==================================================================================
# PRODUCT MASTER
#==================================================================================
class Collateral(models.Model):
    account_no = models.ForeignKey(AccountMaster, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    collateral_code = models.ForeignKey(Basel_Collateral_Master, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    product = models.ForeignKey(Basel_Product_Master, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    collateral_value = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    collateral_rating = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    collateral_residual_maturity = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    edited_on = models.DateTimeField(db_index=True, null=True, blank=True)

#==================================================================================
# EAD INITIAL TABLE
#==================================================================================
class EAD_Initial(models.Model):
    date = models.DateField(auto_now_add=False, null=True, blank=True,)
    account_no = models.ForeignKey(AccountMaster, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    account_no_temp = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    outstanding_amount = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    undrawn_upto_1_yr = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    undrawn_greater_than_1_yr = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    file_identifier = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    created_on = models.DateTimeField(auto_now=True, db_index=True)
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    edited_on = models.DateTimeField(db_index=True, null=True, blank=True)

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" SET_NULL'.format(cls._meta.db_table))

#==================================================================================
# EAD Final TABLE
#==================================================================================
class EAD_Final(models.Model):
    date = models.DateField(auto_now_add=False, null=True, blank=True,)
    account_no = models.ForeignKey(AccountMaster, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    outstanding_amount = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    undrawn_upto_1_yr = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    undrawn_greater_than_1_yr = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True)

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" SET_NULL'.format(cls._meta.db_table))




#==================================================================================
# EAD Report TABLE
#==================================================================================
class EAD_Report(models.Model):
    date = models.DateField(auto_now_add=False, null=True, blank=True,)
    account_no = models.ForeignKey(AccountMaster, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    outstanding_amount = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    undrawn_upto_1_yr = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    undrawn_greater_than_1_yr = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True)
    ead_total = models.CharField(blank=True, null=True, max_length=255, db_index=True)

    def __str__(self):
        return "[{}] - [{}]".format(self.date,self.account_no.account_no)

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" SET_NULL'.format(cls._meta.db_table))


#=================================================================================
#
#=================================================================================

@receiver(post_save, sender=User)
def add_permission(sender, instance, **kwargs):

    try:
        obj = AccessManage.objects.get(user = instance)
    except:
        obj = AccessManage.objects.create(user = instance)

    if instance.is_superuser:
        obj.upload_master_table = True
        obj.edit_master_table = True
        obj.delete_master_table = True
        obj.upload_basel_product = True
        obj.edit_basel_product = True
        obj.delete_basel_product = True
        obj.upload_basel_collateral = True
        obj.edit_basel_collateral = True
        obj.delete_basel_collateral = True
        obj.upload_collateral_mapper = True
        obj.edit_collateral_mapper = True
        obj.delete_collateral_mapper = True
        obj.upload_pd = True
        obj.upload_lgd = True
        obj.upload_ead = True
        obj.upload_ecl = True
        obj.upload_eir = True
        obj.upload_stage = True
        obj.edit_import_pd = True
        obj.edit_import_lgd = True
        obj.edit_import_ead = True
        obj.edit_import_ecl = True
        obj.edit_import_eir = True
        obj.edit_import_stage = True
        obj.delete_import_pd = True
        obj.delete_import_lgd = True
        obj.delete_import_ead = True
        obj.delete_import_ecl = True
        obj.delete_import_eir = True
        obj.delete_import_stage = True
        obj.edit_final_pd = True
        obj.edit_final_lgd = True
        obj.edit_final_ead = True
        obj.edit_final_ecl = True
        obj.edit_final_eir = True
        obj.edit_final_stage = True
        obj.delete_final_pd = True
        obj.delete_final_lgd = True
        obj.delete_final_ead = True
        obj.delete_final_ecl = True
        obj.delete_final_eir = True
        obj.delete_final_stage = True
        obj.run_final_pd = True
        obj.run_final_lgd = True
        obj.run_final_ead = True
        obj.run_final_ecl = True
        obj.run_final_eir = True
        obj.run_final_stage = True
        obj.download_reports_pd = True
        obj.download_reports_lgd = True
        obj.download_reports_ead = True
        obj.download_reports_ecl = True
        obj.download_reports_eir = True
        obj.download_reports_stage = True

    elif instance.is_staff:
        obj.upload_master_table = True
        obj.edit_master_table = True
        obj.delete_master_table = False
        obj.upload_basel_product = True
        obj.edit_basel_product = True
        obj.delete_basel_product = False
        obj.upload_basel_collateral = True
        obj.edit_basel_collateral = True
        obj.delete_basel_collateral = False
        obj.upload_collateral_mapper = True
        obj.edit_collateral_mapper = True
        obj.delete_collateral_mapper = False
        obj.upload_pd = True
        obj.upload_lgd = True
        obj.upload_ead = True
        obj.upload_ecl = True
        obj.upload_eir = True
        obj.upload_stage = True
        obj.edit_import_pd = True
        obj.edit_import_lgd = True
        obj.edit_import_ead = True
        obj.edit_import_ecl = True
        obj.edit_import_eir = True
        obj.edit_import_stage = True
        obj.delete_import_pd = True
        obj.delete_import_lgd = True
        obj.delete_import_ead = True
        obj.delete_import_ecl = True
        obj.delete_import_eir = True
        obj.delete_import_stage = True
        obj.edit_final_pd = True
        obj.edit_final_lgd = True
        obj.edit_final_ead = True
        obj.edit_final_ecl = True
        obj.edit_final_eir = True
        obj.edit_final_stage = True
        obj.delete_final_pd = True
        obj.delete_final_lgd = True
        obj.delete_final_ead = True
        obj.delete_final_ecl = True
        obj.delete_final_eir = True
        obj.delete_final_stage = True
        obj.run_final_pd = True
        obj.run_final_lgd = True
        obj.run_final_ead = True
        obj.run_final_ecl = True
        obj.run_final_eir = True
        obj.run_final_stage = True
        obj.download_reports_pd = True
        obj.download_reports_lgd = True
        obj.download_reports_ead = True
        obj.download_reports_ecl = True
        obj.download_reports_eir = True
        obj.download_reports_stage = True
    else:
        obj.upload_master_table = False
        obj.edit_master_table = False
        obj.delete_master_table = False
        obj.upload_basel_product = False
        obj.edit_basel_product = False
        obj.delete_basel_product = False
        obj.upload_basel_collateral = False
        obj.edit_basel_collateral = False
        obj.delete_basel_collateral = False
        obj.upload_collateral_mapper = False
        obj.edit_collateral_mapper = False
        obj.delete_collateral_mapper = False
        obj.upload_pd = True
        obj.upload_lgd = True
        obj.upload_ead = True
        obj.upload_ecl = True
        obj.upload_eir = True
        obj.upload_stage = True
        obj.edit_import_pd = True
        obj.edit_import_lgd = True
        obj.edit_import_ead = True
        obj.edit_import_ecl = True
        obj.edit_import_eir = True
        obj.edit_import_stage = True
        obj.delete_import_pd = False
        obj.delete_import_lgd = False
        obj.delete_import_ead = False
        obj.delete_import_ecl = False
        obj.delete_import_eir = False
        obj.delete_import_stage = False
        obj.edit_final_pd = True
        obj.edit_final_lgd = True
        obj.edit_final_ead = True
        obj.edit_final_ecl = True
        obj.edit_final_eir = True
        obj.edit_final_stage = True
        obj.delete_final_pd = False
        obj.delete_final_lgd = False
        obj.delete_final_ead = False
        obj.delete_final_ecl = False
        obj.delete_final_eir = False
        obj.delete_final_stage = False
        obj.run_final_pd = True
        obj.run_final_lgd = True
        obj.run_final_ead = True
        obj.run_final_ecl = True
        obj.run_final_eir = True
        obj.run_final_stage = True
        obj.download_reports_pd = True
        obj.download_reports_lgd = True
        obj.download_reports_ead = True
        obj.download_reports_ecl = True
        obj.download_reports_eir = True
        obj.download_reports_stage = True
    obj.save()

#==================================================================================
# PRED DELETE FOR ACCOUNT NUMBERS FROM INITIAL TABLES
#==================================================================================
@receiver(pre_delete, sender=AccountMaster)
def replace_account_nos(sender, instance, **kwargs):
    try:
        AccountMissing.objects.get(account_no = instance.account_no)
    except ObjectDoesNotExist:
        AccountMissing.objects.create(
            account_no = instance.account_no
        )
    except MultipleObjectsReturned:
        AccountMissing.objects.filter(account_no = instance.account_no).delete()
        AccountMissing.objects.create(
            account_no = instance.account_no
        )

    #
    # Update PD INITIAL
    PD_Initial.objects.filter(account_no = instance).update(account_no_temp = instance.account_no, account_no = None)

    #
    # Update LGD INITIAL
    LGD_Initial.objects.filter(account_no = instance).update(account_no_temp = instance.account_no, account_no = None)

    #
    # Update Stage INITIAL
    Stage_Initial.objects.filter(account_no = instance).update(account_no_temp = instance.account_no, account_no = None)

    #
    # Update EIR INITIAL
    EIR_Initial.objects.filter(account_no = instance).update(account_no_temp = instance.account_no, account_no = None)

    #
    # Update ECL INITIAL
    ECL_Initial.objects.filter(account_no = instance).update(account_no_temp = instance.account_no, account_no = None)

    #
    # Update EAD INITIAL
    EAD_Initial.objects.filter(account_no = instance).update(account_no_temp = instance.account_no, account_no = None)


#==================================================================================
# POST SAVE FOR ACCOUNT NUMBERS FROM INITIAL TABLES
#==================================================================================
@receiver(post_save, sender=AccountMaster)
def replace_account_nos(sender, instance, **kwargs):
    try:
        AccountMissing.objects.get(account_no = instance.account_no).delete()
    except:
        pass

    #
    # Update PD INITIAL
    PD_Initial.objects.filter(account_no_temp = instance.account_no).update(account_no_temp = None, account_no = instance)

    #
    # Update LGD INITIAL
    LGD_Initial.objects.filter(account_no_temp = instance.account_no).update(account_no_temp = None, account_no = instance)

    #
    # Update Stage INITIAL
    Stage_Initial.objects.filter(account_no_temp = instance.account_no).update(account_no_temp = None, account_no = instance)

    #
    # Update EIR INITIAL
    EIR_Initial.objects.filter(account_no_temp = instance.account_no).update(account_no_temp = None, account_no = instance)

    #
    # Update ECL INITIAL
    ECL_Initial.objects.filter(account_no = instance).update(account_no_temp = instance.account_no, account_no = None)

    #
    # Update EAD INITIAL
    EAD_Initial.objects.filter(account_no_temp = instance.account_no).update(account_no_temp = None, account_no = instance)


#==================================================================================
# Audit Trail TABLE
#==================================================================================
class Audit_Trail(models.Model):
    date = models.DateField(auto_now_add=False, null=True, blank=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    parent = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    edited_data = models.BooleanField(blank=True, default=False, db_index=True, null=True)
    edited_data_params = models.TextField(blank=True, null=True) # JSON {"table":"initial", selected_ids: [], all:false}
    report_download = models.BooleanField(blank=True, default=False, db_index=True, null=True)
    report_download_params = models.BooleanField(blank=True, default=False, db_index=True, null=True) # JSON {from_initial:false, from_final:false, selected_ids: [], all:false}
    moved_data = models.BooleanField(blank=True, default=False, db_index=True, null=True)
    moved_data_params = models.TextField(blank=True, null=True) # JSON {from_initial:false, selected_ids: [], all:false}
    deleted_data = models.BooleanField(blank=True, default=False, db_index=True, null=True)
    deleted_data_params = models.TextField(blank=True, null=True) # JSON {from_initial:false, from_final:false, from_report:false, selected_ids: [], all:false}
    report_run = models.BooleanField(blank=True, default=False, db_index=True, null=True)
    report_run_params = models.TextField(blank=True, null=True)


#==================================================================================
# ECL INITIAL TABLE
#==================================================================================
class ECL_Initial(models.Model):
    date = models.DateField(auto_now_add=False, null=True, blank=True,)
    account_no = models.ForeignKey(AccountMaster, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    account_no_temp = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    tenure = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    file_identifier = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    created_on = models.DateTimeField(auto_now=True, db_index=True)
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    edited_on = models.DateTimeField(db_index=True, null=True, blank=True)

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" SET_NULL'.format(cls._meta.db_table))


#==================================================================================
# ECL FINAL TABLE
#==================================================================================
class ECL_Final(models.Model):
    date = models.DateField(auto_now_add=False, null=True, blank=True,)
    account_no = models.ForeignKey(AccountMaster, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    tenure = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    file_identifier = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    created_on = models.DateTimeField(auto_now=True, db_index=True)

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" SET_NULL'.format(cls._meta.db_table))


#==================================================================================
# ECL REPORT TABLE
#==================================================================================
class ECL_Reports(models.Model):
    date = models.DateField(auto_now_add=False, null=True, blank=True,)
    account_no = models.ForeignKey(AccountMaster, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    tenure = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    final_ecl = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    eir = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    created_on = models.DateTimeField(auto_now=True, db_index=True)

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" SET_NULL'.format(cls._meta.db_table))


#==================================================================================
# ECL MISSING REPORT TABLE
#==================================================================================
class ECL_Missing_Reports(models.Model):
    date = models.DateField(auto_now_add=False, null=True, blank=True,)
    account_no = models.ForeignKey(AccountMaster, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    tenure = models.CharField(blank=True, null=True, max_length=20, db_index=True)
    pd = models.CharField(blank=True, null=True, max_length=20, db_index=True)
    lgd = models.CharField(blank=True, null=True, max_length=20, db_index=True)
    stage = models.CharField(blank=True, null=True, max_length=20, db_index=True)
    ead = models.CharField(blank=True, null=True, max_length=20, db_index=True)
    eir = models.CharField(blank=True, null=True, max_length=20, db_index=True)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True)

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" SET_NULL'.format(cls._meta.db_table))


#==================================================================================
# EIR - ACCOUNT MAPPER
#==================================================================================
class EIR_Accounts_Mapper(models.Model):
    account_no = models.ForeignKey(AccountMaster, on_delete=models.CASCADE)

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" SET_NULL'.format(cls._meta.db_table))


#==================================================================================
# Predifined TABLE
#==================================================================================
class Pre_Defined_Variables(models.Model):    
    SECTION_CHOICES = (
        ('master', 'master'), 
        ('product', 'product'), 
        ('collateral', 'collateral'), 
        ('pd', 'PD'), 
        ('lgd', 'LGD'), 
        ('ead', 'EAD'), 
        ('stage', 'STAGE'), 
        ('ecl', 'ECL'), 
        ('eir', 'EIR')
    )
    
    tab_status = models.CharField(max_length=255, blank=True, null=True, db_index=True, choices=SECTION_CHOICES)
    column_name = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    show_in_reports = models.BooleanField(default=True, db_index=True)
    show_in_download_reports = models.BooleanField(default=True, db_index=True)
    column_name_in_reports = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    
    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" SET_NULL'.format(cls._meta.db_table))
            
            
#==================================================================================
# PD CONFIG TABLE
#==================================================================================
class Algo_Config(models.Model):
    
    SECTION_CHOICES = (('pd', 'PD'), ('lgd', 'LGD'), ('ead', 'EAD'), ('stage', 'STAGE'), ('ecl', 'ECL'), ('eir', 'EIR'))
    
    tab_status = models.CharField(max_length=255, blank=True, null=True, db_index=True, choices=SECTION_CHOICES)
    column_name = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    use_in_import = models.BooleanField(default=False, db_index=True)
    show_in_reports = models.BooleanField(default=True, db_index=True)
    show_in_download_reports = models.BooleanField(default=True, db_index=True)
    use_as_factor = models.BooleanField(default=False, db_index=True)
    use_formula = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    use_built_in_column = models.ForeignKey(Pre_Defined_Variables, blank=True, null=True, db_index=True, on_delete=models.SET_NULL)
    
    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" SET_NULL'.format(cls._meta.db_table))
            
    
