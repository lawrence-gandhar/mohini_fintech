#
# AUTHOR : LAWRENCE GANDHAR
# Project For Mohini - (India)
# Project Date : 14th Sept 2021
#

from .models import AccountMaster
from .models import PD_Initial
from .models import PD_Final
from .models import LGD_Initial
from .models import LGD_Final
from .models import Stage_Initial
from .models import Stage_Final
from .models import EIR_Initial
from .models import EIR_Final
from .models import EAD_Final
from .models import EAD_Initial
from .models import Basel_Product_Master
from .models import Basel_Collateral_Master
from .models import PD_Report
from .models import LGD_Report
from .models import Stage_Report
from .models import EAD_Report
from .models import EIR_Reports

from .models import ECL_Initial
from .models import ECL_Final
from .models import ECL_Reports

#
# CSV & FIELD HEADERS

ACCOUNT_MASTER_COLS = ['cin', 'account_no', 'account_type', 'account_status', 'sectors', 'customer_name', 'contact_no', 'email', 'pan', 'aadhar_no', 'customer_addr', 'pin']

PD_INITIAL_COLS = ['date', 'account_no', 'factor_1', 'factor_2', 'factor_3', 'factor_4', 'factor_5', 'factor_6', 'default_col', 'mgmt_overlay_1', 'mgmt_overlay_2']

LGD_COLS = ['date', 'account_no', 'ead_os', 'pv_cashflows', 'pv_cost', 'beta_value', 'sec_flag', 'factor_4', 'factor_5', 'avg_1', 'avg_2', 'avg_3', 'avg_4', 'avg_5', 'mgmt_overlay_1', 'mgmt_overlay_2']

STAGE_COLS = ['date', 'account_no', 'old_rating', 'new_rating', 'rating_3', 'rating_4', 'rating_5', 'rating_6', 'rating_7', 'day_bucket_1', 'day_bucket_2', 'day_bucket_3', 'day_bucket_4', 'day_bucket_5', 'day_bucket_6', 'day_bucket_7', 'day_bucket_8', 'day_bucket_9', 'day_bucket_10', 'day_bucket_11', 'day_bucket_12','day_bucket_13', 'day_bucket_14', 'day_bucket_15', 'criteria', 'cooling_period_1', 'cooling_period_2', 'cooling_period_3', 'cooling_period_4', 'cooling_period_5', 'rbi_window', 'mgmt_overlay_1', 'mgmt_overlay_2']

EIR_COLS = ['date', 'account_no', 'period', 'loan_availed', 'cost_avail', 'rate', 'emi', 'os_principal', 'os_interest', 'fair_value', 'coupon', 'discount_factor', 'col_1', 'col_2', 'col_3']

ECL_COLS = ['date', 'account_no', 'tenure']

EAD_COLS = ['date', 'account_no', 'outstanding_amount', 'undrawn_upto_1_yr', 'undrawn_greater_than_1_yr']

BASEL_PRODUCT_COLS = ['product_name', 'product_code', 'product_catgory', 'basel_product', 'basel_product_code', 'drawn_cff', 'cff_upto_1_yr', 'cff_gt_1_yr']

BASEL_COLLATERAL_COLS = ['collateral_code', 'collateral_type', 'issuer_type', 'collateral_eligibity', 'rating_available', 'collateral_rating', 'residual_maturity', 'basel_collateral_type', 'basel_collateral_subtype', 'basel_collateral_code', 'basel_collateral_rating', 'soverign_issuer', 'other_issuer']


#
# CONSTANTS FOR THE APP

TAB_ACTIVE = {
    "master": [
        1,
        "imports/manage_imports_master.html",
        ACCOUNT_MASTER_COLS,
        AccountMaster.objects,
        None,
        None,
        None,
        None,
        None,
    ],
    "pd": [
        2,
        "imports/manage_imports_pd.html",
        PD_INITIAL_COLS,
        PD_Initial.objects,
        PD_Final.objects,
        "app_pd_initial",
        "app_pd_final",
        "output/manage_pd_output.html",
        "reports/pd_reports.html",
        PD_Report.objects,
    ],
    "lgd": [
        3,
        "imports/manage_imports_lgd.html",
        LGD_COLS,
        LGD_Initial.objects,
        LGD_Final.objects,
        "app_lgd_initial",
        "app_lgd_final",
        "output/manage_lgd_output.html",
        "reports/lgd_reports.html",
        LGD_Report.objects,
    ],
    "stage": [
        4,
        "imports/manage_imports_stage.html",
        STAGE_COLS,
        Stage_Initial.objects,
        Stage_Final.objects,
        "app_stage_initial",
        "app_stage_final",
        "output/manage_stage_output.html",
        "reports/stage_reports.html",
        Stage_Report.objects,
    ],
    "eir": [
        5,
        "imports/manage_imports_eir.html",
        EIR_COLS,
        EIR_Initial.objects,
        EIR_Final.objects,
        "app_eir_initial",
        "app_eir_final",
        "output/manage_eir_output.html",
        "reports/eir_reports.html",
        EIR_Reports.objects,
    ],
    "ecl": [
        6,
        "imports/manage_imports_ecl.html",
        ECL_COLS,
        ECL_Initial.objects,
        ECL_Final.objects,
        "app_ecl_initial",
        "app_ecl_final",
        "output/manage_ecl_output.html",
        "reports/ecl_reports.html",
        ECL_Reports.objects,
    ],
    "ead": [
        7,
        "imports/manage_imports_ead.html",
        EAD_COLS,
        EAD_Initial.objects,
        EAD_Final.objects,
        "app_ead_initial",
        "app_ead_final",
        "output/manage_ead_output.html",
        "reports/ead_reports.html",
        EAD_Report.objects,
    ],
    "product": [
        8,
        "imports/manage_imports_products.html",
        BASEL_PRODUCT_COLS,
        Basel_Product_Master.objects,
        None,
        None,
        None,
        None,
        None,
        None,
    ],
    "collateral": [
        9,
        "imports/manage_imports_collateral.html",
        BASEL_COLLATERAL_COLS,
        Basel_Collateral_Master.objects,
        None,
        None,
        None,
        None,
        None,
        None,
    ],
}
