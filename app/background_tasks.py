#
# AUTHOR : LAWRENCE GANDHAR
# Project For Mohini - (India)
# Project Date : 21th Sept 2021
#

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.utils import timezone
from django.db import connection
from django.db.models import F

from . import helpers
from . import constants
from .models import AccountMaster, PD_Report, LGD_Report

import json
import time

import pandas as pd
import numpy as np
import math
from sklearn.linear_model import LogisticRegression, LinearRegression

# **********************************************************************
# METHOD TO MOVE ALL DATA RELEVANT MODELS - BACKGROUND
# **********************************************************************
def move_data_bg_process(request, tab_status=None):

    msg = "No rows to move"
    records_moved = 0
    records_total = 0
    records_failed = 0
    records_valid = 0
    ret = False

    if tab_status in constants.TAB_ACTIVE.keys():

        #constants.TAB_ACTIVE[tab_status][4].all().delete()

        #
        # Queryset
        qry = constants.TAB_ACTIVE[tab_status][3].filter(account_no__isnull = False)

        #
        # Total Records
        records_total = constants.TAB_ACTIVE[tab_status][3].count()

        #
        # Valid Records found for movement
        records_valid = qry.count()

        #
        # If valid records found : then capture & iterate to insert
        if records_valid > 0:

            # Create Insert statement for each tab_status
            if tab_status == "pd":
                result_set = qry.values_list('id', 'date', 'account_no', 'factor_1', 'factor_2', 'factor_3', 'factor_4', 'factor_5', 'factor_6', 'default_col', 'mgmt_overlay_1', 'mgmt_overlay_2')

                insert_qry = """
                    insert into {0} (date, account_no_id, factor_1, factor_2, factor_3, factor_4, factor_5, factor_6, default_col, mgmt_overlay_1, mgmt_overlay_2, created_on)""".format(constants.TAB_ACTIVE[tab_status][6])

                update_qry = """
                    update {0} set factor_1='{3}', factor_2='{4}', factor_3='{5}', factor_4='{6}', factor_5='{7}', factor_6='{8}', default_col='{9}', mgmt_overlay_1='{10}', mgmt_overlay_2='{11}', created_on='{12}' where date='{1}' and account_no_id='{2}'
                    """

            if tab_status == "lgd":
                result_set = qry.values_list('id', 'date', 'account_no', 'ead_os', 'pv_cashflows', 'pv_cost', 'beta_value', 'sec_flag', 'factor_4', 'factor_5', 'avg_1', 'avg_2', 'avg_3', 'avg_4', 'avg_5', 'mgmt_overlay_1', 'mgmt_overlay_2', 'rec_rate')

                insert_qry = """
                    insert into {0} (date, account_no_id, ead_os, pv_cashflows, pv_cost, beta_value, sec_flag, factor_4, factor_5, avg_1, avg_2, avg_3, avg_4, avg_5, mgmt_overlay_1, mgmt_overlay_2, rec_rate, created_on)""".format(constants.TAB_ACTIVE[tab_status][6])

                update_qry = """
                    update {0} set ead_os='{3}', pv_cashflows='{4}', pv_cost='{5}', beta_value='{6}', sec_flag='{7}', factor_4='{8}', factor_5='{9}', avg_1='{10}', avg_2='{11}', avg_3='{12}', avg_4='{13}', avg_5='{14}', mgmt_overlay_1='{15}', mgmt_overlay_2='{16}', rec_rate='{17}', created_on='{18}' where date='{1}' and account_no_id='{2}'
                    """

            if tab_status == "stage":
                result_set = qry.values_list('id', 'date', 'account_no', 'old_rating', 'new_rating', 'rating_3', 'rating_4', 'rating_5', 'rating_6', 'rating_7', 'day_bucket_1', 'day_bucket_2', 'day_bucket_3', 'day_bucket_4', 'day_bucket_5', 'day_bucket_6', 'day_bucket_7', 'day_bucket_8', 'day_bucket_9', 'day_bucket_10', 'day_bucket_11', 'day_bucket_12','day_bucket_13', 'day_bucket_14', 'day_bucket_15', 'criteria', 'cooling_period_1', 'cooling_period_2', 'cooling_period_3', 'cooling_period_4', 'cooling_period_5', 'rbi_window', 'mgmt_overlay_1', 'mgmt_overlay_2')

                insert_qry = """
                    insert into {0} (date, account_no_id, old_rating, new_rating, rating_3, rating_4, rating_5, rating_6, rating_7, day_bucket_1, day_bucket_2, day_bucket_3, day_bucket_4, day_bucket_5, day_bucket_6, day_bucket_7, day_bucket_8, day_bucket_9, day_bucket_10, day_bucket_11, day_bucket_12, day_bucket_13, day_bucket_14, day_bucket_15, criteria, cooling_period_1, cooling_period_2, cooling_period_3, cooling_period_4, cooling_period_5, rbi_window, mgmt_overlay_1, mgmt_overlay_2, created_on)""".format(constants.TAB_ACTIVE[tab_status][6])

                update_qry = """
                    update {0} set old_rating='{3}', new_rating, rating_3='{4}', rating_4='{5}', rating_5='{6}', rating_6='{7}', rating_7='{8}', day_bucket_1='{9}', day_bucket_2='{10}', day_bucket_3='{11}', day_bucket_4='{12}', day_bucket_5='{13}', day_bucket_6='{14}', day_bucket_7='{15}', day_bucket_8='{16}', day_bucket_9='{17}', day_bucket_10='{18}', day_bucket_11='{19}', day_bucket_12='{20}', day_bucket_13='{21}', day_bucket_14='{22}', day_bucket_15='{23}', criteria='{24}', cooling_period_1='{25}', cooling_period_2='{26}', cooling_period_3='{27}', cooling_period_4='{28}', cooling_period_5='{29}', rbi_window='{30}', mgmt_overlay_1='{31}', mgmt_overlay_2='{32}', created_on='{33}' where date='{1}' and account_no_id='{2}'
                """

            #
            # Iterate over each row & insert
            for row in result_set:

                row = list(row)
                row_id = row[0]
                del row[0]

                #
                # update record if already present in final table
                #

                try:
                    ins = constants.TAB_ACTIVE[tab_status][4].get(date = row[0], account_no_id = row[1])

                    with connection.cursor() as cursor:

                        formatted_data = [x if x is not None else '' for x in row]
                        formatted_data.append(timezone.now())

                        update_qry = update_qry.format(constants.TAB_ACTIVE[tab_status][6], *formatted_data)

                        ret_val = False
                        try:
                            cursor.execute(update_qry)
                            records_moved += 1

                            ret_val = True
                        except:
                            records_failed += 1

                        #
                        # Delete record
                        if ret_val:
                            constants.TAB_ACTIVE[tab_status][3].get(pk = row_id).delete()

                except MultipleObjectsReturned:

                    with connection.cursor() as cursor:

                        formatted_data = [x if x is not None else '' for x in row]
                        formatted_data.append(timezone.now())

                        update_qry = update_qry.format(constants.TAB_ACTIVE[tab_status][6], *formatted_data)
                        
                        ret_val = False
                        try:
                            cursor.execute(update_qry)
                            records_moved += 1

                            ret_val = True
                        except:
                            records_failed += 1

                        #
                        # Delete record
                        if ret_val:
                            constants.TAB_ACTIVE[tab_status][3].get(pk = row_id).delete()

                except ObjectDoesNotExist:
                    #
                    # Insert record
                    with connection.cursor() as cursor:

                        formatted_data = [x if x is not None else '' for x in row]
                        formatted_data.append(timezone.now())

                        value_params = "'{}', "*(len(formatted_data))
                        value_params = value_params.rstrip(', ')

                        main_query = insert_qry+"values({})".format(value_params)
                        main_query = main_query.format(*formatted_data)

                        ret_val = False
                        try:
                            cursor.execute(main_query)
                            records_moved += 1

                            ret_val = True
                        except:
                            records_failed += 1

                        #
                        # Delete record
                        if ret_val:
                            constants.TAB_ACTIVE[tab_status][3].get(pk = row_id).delete()

        else:
            msg = "No valid rows to move"


    if records_moved >0 :
        msg = "Records Moved Successfully"
        ret = True

    return dict({
            "ret": ret,
            "msg": msg,
            "total_records": records_total,
            "records_valid": records_valid,
            "no_of_records_moved": records_moved,
            "no_of_records_failed": records_failed
        })


# **********************************************************************
# PD REPORT CALCULATION & DATA LOAD
# **********************************************************************
def pd_report(account_no=None, start_date=None, end_date=None):

    #
    # Loading the data
    results = constants.TAB_ACTIVE["pd"][4]

    if start_date is None and end_date is None and account_no is None:
        results = results.all()

    if start_date is not None:
        if end_date is not None:
            results = results.filter(date__gte = start_date, date__lte = end_date)
        else:
            results = results.filter(date__gte = start_date)

    if account_no is not None:
        results = results.filter(account_no__account_no__in = account_no)

    results = results.select_related("account_no")
    results = results.values('id','date', 'account_no_id', 'factor_1', 'factor_2', 'factor_3', 'factor_4', 'default_col', 'factor_5', 'factor_6', 'mgmt_overlay_1', 'mgmt_overlay_2', Account_No = F('account_no__account_no'))

    if results.exists() is False:
        return False
    else:

        df = pd.DataFrame(results)
        df = df.set_index('id')

        df[["factor_1", "factor_2", "factor_3", "factor_4"]] = df[["factor_1", "factor_2", "factor_3", "factor_4"]].astype(np.float64)
        df["default_col"] = df["default_col"].astype(np.int64)

        x = df[["factor_1", "factor_2", "factor_3", "factor_4"]]
        y = df["default_col"]

        #
        # Extracting intercept and coefficient terms
        logit = LogisticRegression(solver='newton-cg',random_state=0).fit(x,y)

        intercept = logit.intercept_
        coeff = pd.DataFrame(logit.coef_)
        beta1 = coeff[0]
        beta2 = coeff[1]
        beta3 = coeff[2]
        beta4 = coeff[3]

        # Computing Z score and PD values for each account
        df['zscore'] = intercept+ df["factor_1"]*beta1[0]+ df["factor_2"]*beta2[0]+ df["factor_3"]*beta3[0]+ df["factor_4"]*beta4[0]
        df['PD'] = (1/(1+np.exp(-df['zscore'])))

        #
        # Reset Data for insert/update into Report table
        rows = df.to_dict('index')

        for idx, row in rows.items():

            try:
                acc = AccountMaster.objects.get(pk = int(row["account_no_id"]))
            except ObjectDoesNotExist:
                return False

            try:
                pd_report = PD_Report.objects.get(date = row["date"], account_no = acc)

                pd_report.account_type = acc.account_type
                pd_report.cin = acc.cin
                pd_report.product_name = acc.product_name
                pd_report.sectors = acc.sectors
                pd_report.factor_1 = row["factor_1"]
                pd_report.factor_2 = row["factor_2"]
                pd_report.factor_3 = row["factor_3"]
                pd_report.factor_4 = row["factor_4"]
                pd_report.factor_5 = row["factor_5"]
                pd_report.factor_6 = row["factor_6"]
                pd_report.default_col = row["default_col"]
                pd_report.mgmt_overlay_1 = row["mgmt_overlay_1"]
                pd_report.mgmt_overlay_2 = row["mgmt_overlay_2"]
                pd_report.intercept = intercept[0]
                pd_report.coeff_fact1 = beta1[0]
                pd_report.coeff_fact2 = beta2[0]
                pd_report.coeff_fact3 = beta3[0]
                pd_report.coeff_fact4 = beta4[0]
                pd_report.zscore = row["zscore"]
                pd_report.pd = row["PD"]
                pd_report.save()

            except ObjectDoesNotExist:
                pd_report = PD_Report(
                    date = row["date"],
                    account_no = acc,
                    account_type = acc.account_type,
                    cin = acc.cin,
                    product_name = acc.product_name,
                    sectors = acc.sectors,
                    factor_1 = row["factor_1"],
                    factor_2 = row["factor_2"],
                    factor_3 = row["factor_3"],
                    factor_4 = row["factor_4"],
                    factor_5 = row["factor_5"],
                    factor_6 = row["factor_6"],
                    default_col = row["default_col"],
                    mgmt_overlay_1 = row["mgmt_overlay_1"],
                    mgmt_overlay_2 = row["mgmt_overlay_2"],
                    intercept = intercept[0],
                    coeff_fact1 = beta1,
                    coeff_fact2 = beta2,
                    coeff_fact3 = beta3,
                    coeff_fact4 = beta4,
                    zscore = row["zscore"],
                    pd = row["PD"]
                )

                pd_report.save()
        return True


# **********************************************************************
# LGD REPORT CALCULATION & DATA LOAD
# **********************************************************************
def lgd_report(account_no=None, start_date=None, end_date=None):

    #
    # Loading the data
    results = constants.TAB_ACTIVE["lgd"][4].all().select_related("account_no")

    results = results.values('id', 'date', 'account_no_id', 'ead_os', 'pv_cashflows', 'pv_cost', 'beta_value', 'sec_flag', 'factor_4', 'factor_5', 'avg_1', 'avg_2', 'avg_3', 'avg_4', 'avg_5', 'mgmt_overlay_1', 'mgmt_overlay_2', Account_No = F('account_no__account_no'), sectors = F('account_no__sectors'))

    if results.exists() is False:
        return False
    else:
        df = pd.DataFrame(results)
        ddf = df.set_index('id')

        df[["pv_cashflows", "ead_os", "sec_flag", "pv_cost", "beta_value"]] = df[["pv_cashflows", "ead_os", "sec_flag", "pv_cost", "beta_value"]].astype(np.float64)

        df['rec_rate'] = (df["pv_cashflows"]- df["pv_cost"])/df["ead_os"]

        x = df[["beta_value", "sec_flag"]]
        y = df["rec_rate"]

        linmodel = LinearRegression().fit(x,y)
        intercept = linmodel.intercept_
        coeff = pd.DataFrame(linmodel.coef_)
        coeff = coeff.transpose()
        beta1 = coeff[0]
        beta2 = coeff[1]

        # Computing estimated RR and Est_LGD
        df['est_rr'] = intercept+(df['beta_value']*beta1[0])+(df['sec_flag']*beta2[0])
        df['est_lgd'] = 1 - df["est_rr"]

        # Computing LGD
        stats1 = pd.DataFrame(df["est_lgd"].groupby(df["sectors"]).mean())
        stats1.rename(columns = {"est_lgd" : "lgd"}, inplace=True)
        Output_LGD = pd.merge(df, stats1, left_on = 'sectors', right_on = 'sectors', how='outer')

        df['final_lgd'] = ""

        #
        # Reset Data for insert/update into Report table
        rows = df.to_dict('index')

        for idx, row in rows.items():

            try:
                acc = AccountMaster.objects.get(pk = int(row["account_no_id"]))
            except ObjectDoesNotExist:
                return False

            try:
                lgd_report = LGD_Report.objects.get(date = row["date"], account_no = acc)

                lgd_report.account_type = acc.account_type
                lgd_report.cin = acc.cin
                lgd_report.product_name = acc.product_name
                lgd_report.sectors = acc.sectors
                lgd_report.ead_os = row["ead_os"]
                lgd_report.pv_cashflows = row["pv_cashflows"]
                lgd_report.pv_cost = row["pv_cost"]
                lgd_report.beta_value = row["beta_value"]
                lgd_report.sec_flag = row["sec_flag"]
                lgd_report.factor_4 = row["factor_4"]
                lgd_report.factor_5 = row["factor_5"]
                lgd_report.avg_1 = row["avg_1"]
                lgd_report.avg_2 = row["avg_2"]
                lgd_report.avg_3 = row["avg_3"]
                lgd_report.avg_4 = row["avg_4"]
                lgd_report.avg_5 = row["avg_5"]
                lgd_report.mgmt_overlay_1 = row["mgmt_overlay_1"]
                lgd_report.mgmt_overlay_2 = row["mgmt_overlay_2"]
                lgd_report.rec_rate = row["rec_rate"]
                lgd_report.est_rr = row["est_rr"]
                lgd_report.est_lgd = row["est_lgd"]
                lgd_report.final_lgd = row["final_lgd"]
                lgd_report.save()

            except ObjectDoesNotExist:
                lgd_report = LGD_Report(
                    date = row["date"],
                    account_no = acc,
                    account_type = acc.account_type,
                    cin = acc.cin,
                    product_name = acc.product_name,
                    sectors = acc.sectors,
                    ead_os = row["ead_os"],
                    pv_cashflows = row["pv_cashflows"],
                    pv_cost = row["pv_cost"],
                    beta_value = row["beta_value"],
                    sec_flag = row["sec_flag"],
                    factor_4 = row["factor_4"],
                    factor_5 = row["factor_5"],
                    avg_1 = row["avg_1"],
                    avg_2 = row["avg_2"],
                    avg_3 = row["avg_3"],
                    avg_4 = row["avg_4"],
                    avg_5 = row["avg_5"],
                    mgmt_overlay_1 = row["mgmt_overlay_1"],
                    mgmt_overlay_2 = row["mgmt_overlay_2"],
                    rec_rate = row["rec_rate"],
                    est_rr = row["est_rr"],
                    est_lgd = row["est_lgd"],
                    final_lgd = row["final_lgd"]
                )

                lgd_report.save()
        return True


# **********************************************************************
# STAGE REPORT CALCULATION & DATA LOAD
# **********************************************************************

def stage_report(account_no=None, start_date=None, end_date=None):
    #
    # Loading the data
    results = constants.TAB_ACTIVE["stage"][4].all().select_related("account_no")

    results = results.values('id', 'date', 'account_no_id', 'old_rating', 'new_rating', 'rating_3', 'rating_4', 'rating_5', 'rating_6', 'rating_7', 'day_bucket_1', 'day_bucket_2', 'day_bucket_3', 'day_bucket_4', 'day_bucket_5', 'day_bucket_6', 'day_bucket_7', 'day_bucket_8', 'day_bucket_9', 'day_bucket_10', 'day_bucket_11', 'day_bucket_12','day_bucket_13', 'day_bucket_14', 'day_bucket_15', 'criteria', 'cooling_period_1', 'cooling_period_2', 'cooling_period_3', 'cooling_period_4', 'cooling_period_5', 'rbi_window', 'mgmt_overlay_1', 'mgmt_overlay_2', Account_No = F('account_no__account_no'), sectors = F('account_no__sectors'))

    if results.exists() is False:
        return False
    else:

        df = pd.DataFrame(results)
        df = df.set_index('id')

        df["state"] = "No Change"
        df["stage"] = "Stage One"

        for i in range(0, df.shape[0]):
            if((df["old_rating"][i] == "BBB" and df["new_rating"] == "BB") or (df["old_rating"][i] == "BBB" and df["new_rating"] == "BB")):
                df["state"] = "Downgrade"
                df["stage"] = "Stage 2"

            if((df["old_rating"] == "C" or df["old_rating"] == "D") and df["new_rating"]=="D"):
                df["state"] = "Default"
                df["stage"] = "Stage 3"


        #
        # Reset Data for insert/update into Report table
        rows = df.to_dict('index')

        for idx, row in rows.items():

            try:
                acc = AccountMaster.objects.get(pk = int(row["account_no_id"]))
            except ObjectDoesNotExist:
                return False

            try:
                # Edit
                stage_report = Stage_Report.objects.get(date = row["date"], account_no = acc)

                stage_report.account_type = acc.account_type
                stage_report.cin = acc.cin
                stage_report.sectors = acc.sector
                stage_report.product_name = acc.product_name
                stage_report.stage = row["stage"]
                stage_report.state = row["state"]
                stage_report.old_rating = row["old_rating"]
                stage_report.new_rating = row["new_rating"]
                stage_report.rating_3 = row["rating_3"]
                stage_report.rating_4 = row["rating_4"]
                stage_report.rating_5 = row["rating_5"]
                stage_report.rating_6 = row["rating_6"]
                stage_report.rating_7 = row["rating_7"]
                stage_report.day_bucket_1 = row["day_bucket_1"]
                stage_report.day_bucket_2 = row["day_bucket_2"]
                stage_report.day_bucket_3 = row["day_bucket_3"]
                stage_report.day_bucket_4 = row["day_bucket_4"]
                stage_report.day_bucket_5 = row["day_bucket_5"]
                stage_report.day_bucket_6 = row["day_bucket_6"]
                stage_report.day_bucket_7 = row["day_bucket_7"]
                stage_report.day_bucket_8 = row["day_bucket_8"]
                stage_report.day_bucket_9 = row["day_bucket_9"]
                stage_report.day_bucket_10 = row["day_bucket_10"]
                stage_report.day_bucket_11 = row["day_bucket_11"]
                stage_report.day_bucket_12 = row["day_bucket_12"]
                stage_report.day_bucket_13 = row["day_bucket_13"]
                stage_report.day_bucket_14 = row["day_bucket_14"]
                stage_report.day_bucket_15 = row["day_bucket_15"]
                stage_report.criteria = row["criteria"]
                stage_report.cooling_period_1 = row["cooling_period_1"]
                stage_report.cooling_period_2 = row["cooling_period_2"]
                stage_report.cooling_period_3 = row["cooling_period_3"]
                stage_report.cooling_period_4 = row["cooling_period_4"]
                stage_report.cooling_period_5 = row["cooling_period_5"]
                stage_report.rbi_window = row["rbi_window"]
                stage_report.mgmt_overlay_1 = row["mgmt_overlay_1"]
                stage_report.mgmt_overlay_2 = row["mgmt_overlay_2"]

                stage_report.save()
            except:
                # Add
                stage_report = Stage_Report(
                    date = row["date"],
                    account_no = acc,
                    account_type = acc.account_type,
                    cin = acc.cin,
                    sectors = acc.sector,
                    product_name = acc.product_name,
                    stage = row["stage"],
                    state = row["state"],
                    old_rating = row["old_rating"],
                    new_rating = row["new_rating"],
                    rating_3 = row["rating_3"],
                    rating_4 = row["rating_4"],
                    rating_5 = row["rating_5"],
                    rating_6 = row["rating_6"],
                    rating_7 = row["rating_7"],
                    day_bucket_1 = row["day_bucket_1"],
                    day_bucket_2 = row["day_bucket_2"],
                    day_bucket_3 = row["day_bucket_3"],
                    day_bucket_4 = row["day_bucket_4"],
                    day_bucket_5 = row["day_bucket_5"],
                    day_bucket_6 = row["day_bucket_6"],
                    day_bucket_7 = row["day_bucket_7"],
                    day_bucket_8 = row["day_bucket_8"],
                    day_bucket_9 = row["day_bucket_9"],
                    day_bucket_10 = row["day_bucket_10"],
                    day_bucket_11 = row["day_bucket_11"],
                    day_bucket_12 = row["day_bucket_12"],
                    day_bucket_13 = row["day_bucket_13"],
                    day_bucket_14 = row["day_bucket_14"],
                    day_bucket_15 = row["day_bucket_15"],
                    criteria = row["criteria"],
                    cooling_period_1 = row["cooling_period_1"],
                    cooling_period_2 = row["cooling_period_2"],
                    cooling_period_3 = row["cooling_period_3"],
                    cooling_period_4 = row["cooling_period_4"],
                    cooling_period_5 = row["cooling_period_5"],
                    rbi_window = row["rbi_window"],
                    mgmt_overlay_1 = row["mgmt_overlay_1"],
                    mgmt_overlay_2 = row["mgmt_overlay_2"]
                )

                stage_report.save()
                pass
        return True



# **********************************************************************
# PD REPORT CALCULATION & DATA LOAD
# **********************************************************************
def ead_report(account_no=None, start_date=None, end_date=None):

    results = constants.TAB_ACTIVE["stage"][4].all().select_related("account_no")

    results = results.values('id', 'date', 'account_no_id', 'outstanding_amount', 'undrawn_upto_1_yr', 'undrawn_greater_than_1_yr', 'collateral_1_value', 'collateral_1_rating', 'collateral_1_residual_maturity', 'collateral_2_value', 'collateral_2_rating', 'collateral_2_residual_maturity', Account_No = F('account_no__account_no'), sectors = F('account_no__sectors'))

    if results.exists() is False:
        return False
    else:
        return True
