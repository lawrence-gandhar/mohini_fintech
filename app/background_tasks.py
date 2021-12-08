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
from . models import *

import json
import time

import pandas as pd
import numpy as np
import math
from sklearn.linear_model import LogisticRegression, LinearRegression


#**********************************************************************
# METHOD TO INSERT DATA INTO RELEVANT MODELS
#**********************************************************************
def insert_data(data_set, import_type, file_identifier=None):

    for row in data_set:
        col_names = row.keys()

        try:
            account_ins = AccountMaster.objects.get(account_no = row["account_no"].strip())
        except ObjectDoesNotExist:
            account_ins = None
        except KeyError:
            account_ins = None

        try:
            if import_type == "master":
                if account_ins is None:
                    raise Exception("exception")
                else:
                    update_record(account_ins, import_type, row, file_identifier)
            elif import_type == "product" and row["product_code"].strip()!="":
                ins_const = constants.TAB_ACTIVE[import_type][3].get(product_code = row["product_code"].strip())
            elif import_type == "collateral" and row["basel_collateral_code"].strip()!="":
                ins_const = constants.TAB_ACTIVE[import_type][3].get(basel_collateral_code = row["basel_collateral_code"].strip())
            else:
                if account_ins is not None:
                    ins_const = constants.TAB_ACTIVE[import_type][3].get(account_no = account_ins, date = row["date"])
                else:
                    ins_const = constants.TAB_ACTIVE[import_type][3].get(account_no_temp = row["account_no"].strip(), date = row["date"].strip())

                update_record(ins_const, import_type, row, file_identifier)

        except:

            #
            # MASTER ENTRY
            if import_type == "master" and account_ins is None:
                ins = AccountMaster.objects.create(
                    cin = row["cin"] if row["cin"].strip()!="" else None if "cin" in col_names else None,
                    account_no = row["account_no"] if row["account_no"].strip()!="" else None if "account_no" in col_names else None,
                    account_type = row["account_type"] if row["account_type"].strip()!="" else None if "account_type" in col_names else None,
                    account_status = row["account_status"] if row["account_status"].strip()!="" else None if "account_status" in col_names else None,
                    sectors = row["sectors"] if row["sectors"].strip()!="" else None if "sectors" in col_names else None,
                    customer_name = row["customer_name"] if row["customer_name"].strip()!="" else None if "customer_name" in col_names else None,
                    contact_no = row["contact_no"] if row["contact_no"].strip()!="" else None if "contact_no" in col_names else None,
                    email = row["email"] if row["email"].strip()!="" else None if "email" in col_names else None,
                    pan = row["pan"] if row["pan"].strip()!="" else None if "pan" in col_names else None,
                    aadhar_no = row["aadhar_no"] if row["aadhar_no"].strip()!="" else None if "aadhar_no" in col_names else None,
                    customer_addr = row["customer_addr"] if row["customer_addr"].strip()!="" else None if "customer_addr" in col_names else None,
                    pin = row["pin"] if row["pin"].strip()!="" else None if "pin" in col_names else None,
                )

            #
            # BASEL PRODUCT ENTRY
            if import_type == "product" and row["product_code"].strip()!="":
                ins = Basel_Product_Master.objects.create(
                    product_name = row["product_name"] if row["product_name"].strip()!="" else None if "product_name" in col_names else None,
                    product_code = row["product_code"] if row["product_code"].strip()!="" else None if "product_code" in col_names else None,
                    product_catgory = row["product_catgory"] if row["product_catgory"].strip()!="" else None if "product_catgory" in col_names else None,
                    basel_product = row["basel_product"] if row["basel_product"].strip()!="" else None if "basel_product" in col_names else None,
                    basel_product_code = row["basel_product_code"] if row["basel_product_code"].strip()!="" else None if "basel_product_code" in col_names else None,
                    drawn_cff = row["drawn_cff"] if row["drawn_cff"].strip()!="" else None if "drawn_cff" in col_names else None,
                    cff_upto_1_yr = row["cff_upto_1_yr"] if row["cff_upto_1_yr"].strip()!="" else None if "cff_upto_1_yr" in col_names else None,
                    cff_gt_1_yr = row["cff_gt_1_yr"] if row["cff_gt_1_yr"].strip()!="" else None if "cff_gt_1_yr" in col_names else None,
                )

            #
            # BASEL PRODUCT ENTRY
            if import_type == "collateral" and row["basel_collateral_code"].strip()!="":
                ins = Basel_Collateral_Master.objects.create(
                    basel_collateral_code = row["basel_collateral_code"] if row["basel_collateral_code"].strip()!="" else None if "basel_collateral_code" in col_names else None,
                    collateral_code = row["collateral_code"] if row["collateral_code"].strip()!="" else None if "collateral_code" in col_names else None,
                    collateral_type = row["collateral_type"] if row["collateral_type"].strip()!="" else None if "collateral_type" in col_names else None,
                    issuer_type = row["issuer_type"] if row["issuer_type"].strip()!="" else None if "issuer_type" in col_names else None,
                    collateral_eligibity = row["collateral_eligibity"] if row["collateral_eligibity"].strip()!="" else None if "collateral_eligibity" in col_names else None,
                    rating_available = row["rating_available"] if row["rating_available"].strip()!="" else None if "rating_available" in col_names else None,
                    collateral_rating = row["collateral_rating"] if row["collateral_rating"].strip()!="" else None if "collateral_rating" in col_names else None,
                    residual_maturity = row["residual_maturity"] if row["residual_maturity"].strip()!="" else None if "residual_maturity" in col_names else None,
                    basel_collateral_type = row["basel_collateral_type"] if row["basel_collateral_type"].strip()!="" else None if "basel_collateral_type" in col_names else None,
                    basel_collateral_subtype = row["basel_collateral_subtype"] if row["basel_collateral_subtype"].strip()!="" else None if "basel_collateral_subtype" in col_names else None,

                    basel_collateral_rating = row["basel_collateral_rating"] if row["basel_collateral_rating"].strip()!="" else None if "basel_collateral_rating" in col_names else None,
                    soverign_issuer = row["soverign_issuer"] if row["soverign_issuer"].strip()!="" else None if "soverign_issuer" in col_names else None,
                    other_issuer = row["other_issuer"] if row["other_issuer"].strip()!="" else None if "other_issuer" in col_names else None,
                )

            #
            # PD
            if import_type == "pd":

                ins = PD_Initial.objects.create(
                 date = helpers.clean_data(row["date"]) if "date" in col_names else None,
                 factor_1 = helpers.clean_data(row["factor_1"]) if "factor_1" in col_names else None,
                 factor_2 = helpers.clean_data(row["factor_2"]) if "factor_2" in col_names else None,
                 factor_3 = helpers.clean_data(row["factor_3"]) if "factor_3" in col_names else None,
                 factor_4 = helpers.clean_data(row["factor_4"]) if "factor_4" in col_names else None,
                 factor_5 = helpers.clean_data(row["factor_5"]) if "factor_5" in col_names else None,
                 factor_6 = helpers.clean_data(row["factor_6"]) if "factor_6" in col_names else None,
                 default_col = helpers.clean_data(row["default_col"]) if "default_col" in col_names else None,
                 mgmt_overlay_1 = helpers.clean_data(row["mgmt_overlay_1"]) if "mgmt_overlay_1" in col_names else None,
                 mgmt_overlay_2 = helpers.clean_data(row["mgmt_overlay_2"]) if "mgmt_overlay_2" in col_names else None,
                )

            #
            # LGD
            if import_type == "lgd":
                ins = LGD_Initial.objects.create(
                 date = helpers.clean_data(row["date"]) if "date" in col_names else None,
                 ead_os = helpers.clean_data(row["ead_os"]) if "ead_os" in col_names else None,
                 pv_cashflows = helpers.clean_data(row["pv_cashflows"]) if "pv_cashflows" in col_names else None,
                 pv_cost = helpers.clean_data(row["pv_cost"]) if "pv_cost" in col_names else None,
                 beta_value = helpers.clean_data(row["beta_value"]) if "beta_value" in col_names else None,
                 sec_flag = helpers.clean_data(row["sec_flag"]) if "sec_flag" in col_names else None,
                 factor_4 = helpers.clean_data(row["factor_4"]) if "factor_4" in col_names else None,
                 factor_5 = helpers.clean_data(row["factor_5"]) if "factor_5" in col_names else None,
                 avg_1 = helpers.clean_data(row["avg_1"]) if "avg_1" in col_names else None,
                 avg_2 = helpers.clean_data(row["avg_2"]) if "avg_2" in col_names else None,
                 avg_3 = helpers.clean_data(row["avg_3"]) if "avg_3" in col_names else None,
                 avg_4 = helpers.clean_data(row["avg_4"]) if "avg_4" in col_names else None,
                 avg_5 = helpers.clean_data(row["avg_5"]) if "avg_5" in col_names else None,
                 mgmt_overlay_1 = helpers.clean_data(row["mgmt_overlay_1"]) if "mgmt_overlay_1" in col_names else None,
                 mgmt_overlay_2 = helpers.clean_data(row["mgmt_overlay_2"]) if "mgmt_overlay_2" in col_names else None,
                )

            #
            # STAGE
            if import_type == "stage":
                ins = Stage_Initial.objects.create(
                 date = helpers.clean_data(row["date"]) if "date" in col_names else None,
                 old_rating = helpers.clean_data(row["old_rating"]) if "old_rating" in col_names else None,
                 new_rating = helpers.clean_data(row["new_rating"]) if "new_rating" in col_names else None,
                 rating_3 = helpers.clean_data(row["rating_3"]) if "rating_3" in col_names else None,
                 rating_4 = helpers.clean_data(row["rating_4"]) if "rating_4" in col_names else None,
                 rating_5 = helpers.clean_data(row["rating_5"]) if "rating_5" in col_names else None,
                 rating_6 = helpers.clean_data(row["rating_6"]) if "rating_6" in col_names else None,
                 rating_7 = helpers.clean_data(row["rating_7"]) if "rating_7" in col_names else None,
                 day_bucket_1 = helpers.clean_data(row["day_bucket_1"]) if "day_bucket_1" in col_names else None,
                 day_bucket_2 = helpers.clean_data(row["day_bucket_2"]) if "day_bucket_2" in col_names else None,
                 day_bucket_3 = helpers.clean_data(row["day_bucket_3"]) if "day_bucket_3" in col_names else None,
                 day_bucket_4 = helpers.clean_data(row["day_bucket_4"]) if "day_bucket_4" in col_names else None,
                 day_bucket_5 = helpers.clean_data(row["day_bucket_5"]) if "day_bucket_5" in col_names else None,
                 day_bucket_6 = helpers.clean_data(row["day_bucket_6"]) if "day_bucket_6" in col_names else None,
                 day_bucket_7 = helpers.clean_data(row["day_bucket_7"]) if "day_bucket_7" in col_names else None,
                 day_bucket_8 = helpers.clean_data(row["day_bucket_8"]) if "day_bucket_8" in col_names else None,
                 day_bucket_9 = helpers.clean_data(row["day_bucket_9"]) if "day_bucket_9" in col_names else None,
                 day_bucket_10 = helpers.clean_data(row["day_bucket_10"]) if "day_bucket_10" in col_names else None,
                 day_bucket_11 = helpers.clean_data(row["day_bucket_11"]) if "day_bucket_11" in col_names else None,
                 day_bucket_12 = helpers.clean_data(row["day_bucket_12"]) if "day_bucket_12" in col_names else None,
                 day_bucket_13 = helpers.clean_data(row["day_bucket_13"]) if "day_bucket_13" in col_names else None,
                 day_bucket_14 = helpers.clean_data(row["day_bucket_14"]) if "day_bucket_14" in col_names else None,
                 day_bucket_15 = helpers.clean_data(row["day_bucket_15"]) if "day_bucket_15" in col_names else None,
                 criteria = helpers.clean_data(row["criteria"]) if "criteria" in col_names else None,
                 cooling_period_1 = helpers.clean_data(row["cooling_period_1"]) if "cooling_period_1" in col_names else None,
                 cooling_period_2 = helpers.clean_data(row["cooling_period_2"]) if "cooling_period_2" in col_names else None,
                 cooling_period_3 = helpers.clean_data(row["cooling_period_3"]) if "cooling_period_3" in col_names else None,
                 cooling_period_4 = helpers.clean_data(row["cooling_period_4"]) if "cooling_period_4" in col_names else None,
                 cooling_period_5 = helpers.clean_data(row["cooling_period_5"]) if "cooling_period_5" in col_names else None,
                 rbi_window = helpers.clean_data(row["rbi_window"]) if "rbi_window" in col_names else None,
                 mgmt_overlay_1 = helpers.clean_data(row["mgmt_overlay_1"]) if "mgmt_overlay_1" in col_names else None,
                 mgmt_overlay_2 = helpers.clean_data(row["mgmt_overlay_2"]) if "mgmt_overlay_2" in col_names else None,
                )

            #
            #
            if import_type == "ead":
                ins = EAD_Initial.objects.create(
                    date = helpers.clean_data(row["date"]) if "date" in col_names else None,
                    outstanding_amount = helpers.clean_data(row["outstanding_amount"]) if "outstanding_amount" in col_names else None,
                    undrawn_upto_1_yr = helpers.clean_data(row["undrawn_upto_1_yr"]) if "undrawn_upto_1_yr" in col_names else None,
                    undrawn_greater_than_1_yr = helpers.clean_data(row["undrawn_greater_than_1_yr"]) if "undrawn_greater_than_1_yr" in col_names else None,
                    collateral_1_value = helpers.clean_data(row["collateral_1_value"]) if "collateral_1_value" in col_names else None,
                    collateral_1_rating = helpers.clean_data(row["collateral_1_rating"]) if "collateral_1_rating" in col_names else None,
                    collateral_1_residual_maturity = helpers.clean_data(row["collateral_1_residual_maturity"]) if "collateral_1_residual_maturity" in col_names else None,
                    collateral_2_value = helpers.clean_data(row["collateral_2_value"]) if "collateral_2_value" in col_names else None,
                    collateral_2_rating = helpers.clean_data(row["collateral_2_rating"]) if "collateral_2_rating" in col_names else None,
                    collateral_2_residual_maturity = helpers.clean_data(row["collateral_2_residual_maturity"]) if "collateral_2_residual_maturity" in col_names else None,
                )

            #
            # Fetch Account Number Instance
            if account_ins is not None and (import_type not in ["master", "product", "collateral"]):
                ins.account_no = account_ins
            else:
                if "account_no" in col_names and (import_type not in ["master", "product", "collateral"]):
                    if row["account_no"].strip()!="":
                        ins.account_no_temp = row["account_no"]
                        _, created = AccountMissing.objects.update_or_create(
                            account_no = row["account_no"]
                        )
            #
            # add file Identifier
            try:
                ins.file_identifier = file_identifier
                ins.save()
            except:
                pass


#**********************************************************************
# METHOD TO UPDATE DATA INTO RELEVANT MODELS
#**********************************************************************
def update_record(ins_const=None, import_type=None, row=None, file_identifier=None):

    col_names = row.keys()
    #
    # MASTER ENTRY
    if import_type == "master":

        ins_const.cin = row["cin"] if row["cin"].strip()!="" else None if "cin" in col_names else None
        ins_const.account_no = row["account_no"] if row["account_no"].strip()!="" else None if "account_no" in col_names else None
        ins_const.account_type = row["account_type"] if row["account_type"].strip()!="" else None if "account_type" in col_names else None
        ins_const.account_status = row["account_status"] if row["account_status"].strip()!="" else None if "account_status" in col_names else None
        ins_const.sectors = row["sectors"] if row["sectors"].strip()!="" else None if "sectors" in col_names else None
        ins_const.customer_name = row["customer_name"] if row["customer_name"].strip()!="" else None if "customer_name" in col_names else None
        ins_const.contact_no = row["contact_no"] if row["contact_no"].strip()!="" else None if "contact_no" in col_names else None
        ins_const.email = row["email"] if row["email"].strip()!="" else None if "email" in col_names else None
        ins_const.pan = row["pan"] if row["pan"].strip()!="" else None if "pan" in col_names else None
        ins_const.aadhar_no = row["aadhar_no"] if row["aadhar_no"].strip()!="" else None if "aadhar_no" in col_names else None
        ins_const.customer_addr = row["customer_addr"] if row["customer_addr"].strip()!="" else None if "customer_addr" in col_names else None
        ins_const.pin = row["pin"] if row["pin"].strip()!="" else None if "pin" in col_names else None

    #
    # BASEL PRODUCT ENTRY
    if import_type == "product" and row["product_code"].strip()!="":

        ins_const.product_name = row["product_name"] if row["product_name"].strip()!="" else None if "product_name" in col_names else None
        ins_const.product_code = row["product_code"] if row["product_code"].strip()!="" else None if "product_code" in col_names else None
        ins_const.product_catgory = row["product_catgory"] if row["product_catgory"].strip()!="" else None if "product_catgory" in col_names else None
        ins_const.basel_product = row["basel_product"] if row["basel_product"].strip()!="" else None if "basel_product" in col_names else None
        ins_const.basel_product_code = row["basel_product_code"] if row["basel_product_code"].strip()!="" else None if "basel_product_code" in col_names else None
        ins_const.drawn_cff = row["drawn_cff"] if row["drawn_cff"].strip()!="" else None if "drawn_cff" in col_names else None
        ins_const.cff_upto_1_yr = row["cff_upto_1_yr"] if row["cff_upto_1_yr"].strip()!="" else None if "cff_upto_1_yr" in col_names else None
        ins_const.cff_gt_1_yr = row["cff_gt_1_yr"] if row["cff_gt_1_yr"].strip()!="" else None if "cff_gt_1_yr" in col_names else None


    #
    # BASEL COLLATERAL ENTRY
    if import_type == "collateral" and row["basel_collateral_code"].strip()!="":
        ins_const.basel_collateral_code = row["basel_collateral_code"] if row["basel_collateral_code"].strip()!="" else None if "basel_collateral_code" in col_names else None
        ins_const.collateral_code = row["collateral_code"] if row["collateral_code"].strip()!="" else None if "collateral_code" in col_names else None
        ins_const.collateral_type = row["collateral_type"] if row["collateral_type"].strip()!="" else None if "collateral_type" in col_names else None
        ins_const.issuer_type = row["issuer_type"] if row["issuer_type"].strip()!="" else None if "issuer_type" in col_names else None
        ins_const.collateral_eligibity = row["collateral_eligibity"] if row["collateral_eligibity"].strip()!="" else None if "collateral_eligibity" in col_names else None
        ins_const.rating_available = row["rating_available"] if row["rating_available"].strip()!="" else None if "rating_available" in col_names else None
        ins_const.collateral_rating = row["collateral_rating"] if row["collateral_rating"].strip()!="" else None if "collateral_rating" in col_names else None
        ins_const.residual_maturity = row["residual_maturity"] if row["residual_maturity"].strip()!="" else None if "residual_maturity" in col_names else None
        ins_const.basel_collateral_type = row["basel_collateral_type"] if row["basel_collateral_type"].strip()!="" else None if "basel_collateral_type" in col_names else None
        ins_const.basel_collateral_subtype = row["basel_collateral_subtype"] if row["basel_collateral_subtype"].strip()!="" else None if "basel_collateral_subtype" in col_names else None
        ins_const.basel_collateral_rating = row["basel_collateral_rating"] if row["basel_collateral_rating"].strip()!="" else None if "basel_collateral_rating" in col_names else None
        ins_const.soverign_issuer = row["soverign_issuer"] if row["soverign_issuer"].strip()!="" else None if "soverign_issuer" in col_names else None
        ins_const.other_issuer = row["other_issuer"] if row["other_issuer"].strip()!="" else None if "other_issuer" in col_names else None


    #
    # PD
    if import_type == "pd":

         ins_const.date = helpers.clean_data(row["date"]) if "date" in col_names else None
         ins_const.factor_1 = helpers.clean_data(row["factor_1"]) if "factor_1" in col_names else None
         ins_const.factor_2 = helpers.clean_data(row["factor_2"]) if "factor_2" in col_names else None
         ins_const.factor_3 = helpers.clean_data(row["factor_3"]) if "factor_3" in col_names else None
         ins_const.factor_4 = helpers.clean_data(row["factor_4"]) if "factor_4" in col_names else None
         ins_const.factor_5 = helpers.clean_data(row["factor_5"]) if "factor_5" in col_names else None
         ins_const.factor_6 = helpers.clean_data(row["factor_6"]) if "factor_6" in col_names else None
         ins_const.default_col = helpers.clean_data(row["default_col"]) if "default_col" in col_names else None
         ins_const.mgmt_overlay_1 = helpers.clean_data(row["mgmt_overlay_1"]) if "mgmt_overlay_1" in col_names else None
         ins_const.mgmt_overlay_2 = helpers.clean_data(row["mgmt_overlay_2"]) if "mgmt_overlay_2" in col_names else None

    #
    # LGD
    if import_type == "lgd":

         ins_const.date = helpers.clean_data(row["date"]) if "date" in col_names else None
         ins_const.ead_os = helpers.clean_data(row["ead_os"]) if "ead_os" in col_names else None,
         ins_const.pv_cashflows = helpers.clean_data(row["pv_cashflows"]) if "pv_cashflows" in col_names else None
         ins_const.pv_cost = helpers.clean_data(row["pv_cost"]) if "pv_cost" in col_names else None
         ins_const.beta_value = helpers.clean_data(row["beta_value"]) if "beta_value" in col_names else None
         ins_const.sec_flag = helpers.clean_data(row["sec_flag"]) if "sec_flag" in col_names else None
         ins_const.factor_4 = helpers.clean_data(row["factor_4"]) if "factor_4" in col_names else None
         ins_const.factor_5 = helpers.clean_data(row["factor_5"]) if "factor_5" in col_names else None
         ins_const.avg_1 = helpers.clean_data(row["avg_1"]) if "avg_1" in col_names else None
         ins_const.avg_2 = helpers.clean_data(row["avg_2"]) if "avg_2" in col_names else None
         ins_const.avg_3 = helpers.clean_data(row["avg_3"]) if "avg_3" in col_names else None
         ins_const.avg_4 = helpers.clean_data(row["avg_4"]) if "avg_4" in col_names else None
         ins_const.avg_5 = helpers.clean_data(row["avg_5"]) if "avg_5" in col_names else None
         ins_const.mgmt_overlay_1 = helpers.clean_data(row["mgmt_overlay_1"]) if "mgmt_overlay_1" in col_names else None
         ins_const.mgmt_overlay_2 = helpers.clean_data(row["mgmt_overlay_2"]) if "mgmt_overlay_2" in col_names else None

    #
    # STAGE
    if import_type == "stage":

         ins_const.date = helpers.clean_data(row["date"]) if "date" in col_names else None
         ins_const.old_rating = helpers.clean_data(row["old_rating"]) if "old_rating" in col_names else None
         ins_const.new_rating = helpers.clean_data(row["new_rating"]) if "new_rating" in col_names else None
         ins_const.rating_3 = helpers.clean_data(row["rating_3"]) if "rating_3" in col_names else None
         ins_const.rating_4 = helpers.clean_data(row["rating_4"]) if "rating_4" in col_names else None
         ins_const.rating_5 = helpers.clean_data(row["rating_5"]) if "rating_5" in col_names else None
         ins_const.rating_6 = helpers.clean_data(row["rating_6"]) if "rating_6" in col_names else None
         ins_const.rating_7 = helpers.clean_data(row["rating_7"]) if "rating_7" in col_names else None
         ins_const.day_bucket_1 = helpers.clean_data(row["day_bucket_1"]) if "day_bucket_1" in col_names else None
         ins_const.day_bucket_2 = helpers.clean_data(row["day_bucket_2"]) if "day_bucket_2" in col_names else None
         ins_const.day_bucket_3 = helpers.clean_data(row["day_bucket_3"]) if "day_bucket_3" in col_names else None
         ins_const.day_bucket_4 = helpers.clean_data(row["day_bucket_4"]) if "day_bucket_4" in col_names else None
         ins_const.day_bucket_5 = helpers.clean_data(row["day_bucket_5"]) if "day_bucket_5" in col_names else None
         ins_const.day_bucket_6 = helpers.clean_data(row["day_bucket_6"]) if "day_bucket_6" in col_names else None
         ins_const.day_bucket_7 = helpers.clean_data(row["day_bucket_7"]) if "day_bucket_7" in col_names else None
         ins_const.day_bucket_8 = helpers.clean_data(row["day_bucket_8"]) if "day_bucket_8" in col_names else None
         ins_const.day_bucket_9 = helpers.clean_data(row["day_bucket_9"]) if "day_bucket_9" in col_names else None
         ins_const.day_bucket_10 = helpers.clean_data(row["day_bucket_10"]) if "day_bucket_10" in col_names else None
         ins_const.day_bucket_11 = helpers.clean_data(row["day_bucket_11"]) if "day_bucket_11" in col_names else None
         ins_const.day_bucket_12 = helpers.clean_data(row["day_bucket_12"]) if "day_bucket_12" in col_names else None
         ins_const.day_bucket_13 = helpers.clean_data(row["day_bucket_13"]) if "day_bucket_13" in col_names else None
         ins_const.day_bucket_14 = helpers.clean_data(row["day_bucket_14"]) if "day_bucket_14" in col_names else None
         ins_const.day_bucket_15 = helpers.clean_data(row["day_bucket_15"]) if "day_bucket_15" in col_names else None
         ins_const.criteria = helpers.clean_data(row["criteria"]) if "criteria" in col_names else None
         ins_const.cooling_period_1 = helpers.clean_data(row["cooling_period_1"]) if "cooling_period_1" in col_names else None
         ins_const.cooling_period_2 = helpers.clean_data(row["cooling_period_2"]) if "cooling_period_2" in col_names else None
         ins_const.cooling_period_3 = helpers.clean_data(row["cooling_period_3"]) if "cooling_period_3" in col_names else None
         ins_const.cooling_period_4 = helpers.clean_data(row["cooling_period_4"]) if "cooling_period_4" in col_names else None
         ins_const.cooling_period_5 = helpers.clean_data(row["cooling_period_5"]) if "cooling_period_5" in col_names else None
         ins_const.rbi_window = helpers.clean_data(row["rbi_window"]) if "rbi_window" in col_names else None
         ins_const.mgmt_overlay_1 = helpers.clean_data(row["mgmt_overlay_1"]) if "mgmt_overlay_1" in col_names else None
         ins_const.mgmt_overlay_2 = helpers.clean_data(row["mgmt_overlay_2"]) if "mgmt_overlay_2" in col_names else None

    #
    #
    if import_type == "ead":

        ins_const.date = helpers.clean_data(row["date"]) if "date" in col_names else None
        ins_const.outstanding_amount = helpers.clean_data(row["outstanding_amount"]) if "outstanding_amount" in col_names else None
        ins_const.undrawn_upto_1_yr = helpers.clean_data(row["undrawn_upto_1_yr"]) if "undrawn_upto_1_yr" in col_names else None
        ins_const.undrawn_greater_than_1_yr = helpers.clean_data(row["undrawn_greater_than_1_yr"]) if "undrawn_greater_than_1_yr" in col_names else None
        ins_const.collateral_1_value = helpers.clean_data(row["collateral_1_value"]) if "collateral_1_value" in col_names else None
        ins_const.collateral_1_rating = helpers.clean_data(row["collateral_1_rating"]) if "collateral_1_rating" in col_names else None
        ins_const.collateral_1_residual_maturity = helpers.clean_data(row["collateral_1_residual_maturity"]) if "collateral_1_residual_maturity" in col_names else None
        ins_const.collateral_2_value = helpers.clean_data(row["collateral_2_value"]) if "collateral_2_value" in col_names else None
        ins_const.collateral_2_rating = helpers.clean_data(row["collateral_2_rating"]) if "collateral_2_rating" in col_names else None
        ins_const.collateral_2_residual_maturity = helpers.clean_data(row["collateral_2_residual_maturity"]) if "collateral_2_residual_maturity" in col_names else None

    #
    # Fetch Account Number Instance
    if "account_no" in col_names and (import_type not in ["master", "product", "collateral"]):
        if row["account_no"].strip()!="":
            try:
                account_ins = AccountMaster.objects.get(account_no = row["account_no"].strip())
                ins_const.account_no = account_ins
            except ObjectDoesNotExist:
                ins_const.account_no_temp = row["account_no"]
                _, created = AccountMissing.objects.update_or_create(
                    account_no = row["account_no"]
                )
    #
    # add file Identifier
    ins_const.file_identifier = file_identifier
    ins_const.save()


#**********************************************************************
# PRIVATE METHOD TO MOVE RECORD:
# USED IN @move_to_final and @move_all_to_final
# @obj is the instance of the queryset
#**********************************************************************
def move_record(tab_status=None, obj=None):

    if tab_status == "pd" and obj is not None:
        constants.TAB_ACTIVE[tab_status][4].create(
            date = obj.date,
            account_no = obj.account_no,
            factor_1 = obj.factor_1,
            factor_2 = obj.factor_2,
            factor_3 = obj.factor_3,
            factor_4 = obj.factor_4,
            factor_5 = obj.factor_5,
            factor_6 = obj.factor_6,
            default_col = obj.default_col,
            mgmt_overlay_1 = obj.mgmt_overlay_1,
            mgmt_overlay_2 = obj.mgmt_overlay_2,
        )

        obj.delete()
        return True

    elif tab_status == "lgd" and obj is not None:
        constants.TAB_ACTIVE[tab_status][4].create(
            date = obj.date,
            account_no = obj.account_no,
            ead_os = obj.ead_os,
            pv_cashflows = obj.pv_cashflows,
            pv_cost = obj.pv_cost,
            beta_value = obj.beta_value,
            sec_flag = obj.sec_flag,
            factor_4 = obj.factor_4,
            factor_5 = obj.factor_5,
            avg_1 = obj.avg_1,
            avg_2 = obj.avg_2,
            avg_3 = obj.avg_3,
            avg_4 = obj.avg_4,
            avg_5 = obj.avg_5,
            mgmt_overlay_1 = obj.mgmt_overlay_1,
            mgmt_overlay_2 = obj.mgmt_overlay_2,
        )

        obj.delete()
        return True

    elif tab_status == "stage" and obj is not None:
        constants.TAB_ACTIVE[tab_status][4].create(
            date = obj.date,
            account_no = obj.account_no,
            old_rating = obj.old_rating,
            new_rating = obj.new_rating,
            rating_3 = obj.rating_3,
            rating_4 = obj.rating_4,
            rating_5 = obj.rating_5,
            rating_6 = obj.rating_6,
            rating_7 = obj.rating_7,
            day_bucket_1 = obj.day_bucket_1,
            day_bucket_2 = obj.day_bucket_2,
            day_bucket_3 = obj.day_bucket_3,
            day_bucket_4 = obj.day_bucket_4,
            day_bucket_5 = obj.day_bucket_5,
            day_bucket_6 = obj.day_bucket_6,
            day_bucket_7 = obj.day_bucket_7,
            day_bucket_8 = obj.day_bucket_8,
            day_bucket_9 = obj.day_bucket_9,
            day_bucket_10 = obj.day_bucket_10,
            day_bucket_11 = obj.day_bucket_11,
            day_bucket_12 = obj.day_bucket_12,
            day_bucket_13 = obj.day_bucket_13,
            day_bucket_14 = obj.day_bucket_14,
            day_bucket_15 = obj.day_bucket_15,
            criteria = obj.criteria,
            cooling_period_1 = obj.cooling_period_1,
            cooling_period_2 = obj.cooling_period_2,
            cooling_period_3 = obj.cooling_period_3,
            cooling_period_4 = obj.cooling_period_4,
            cooling_period_5 = obj.cooling_period_5,
            rbi_window = obj.rbi_window,
            mgmt_overlay_1 = obj.mgmt_overlay_1,
            mgmt_overlay_2 = obj.mgmt_overlay_2
        )

        obj.delete()
        return True

    elif tab_status == "ead" and obj is not None:
        constants.TAB_ACTIVE[tab_status][4].create(
            date = obj.date,
            account_no = obj.account_no,
            outstanding_amount = obj.outstanding_amount,
            undrawn_upto_1_yr = obj.undrawn_upto_1_yr,
            undrawn_greater_than_1_yr = obj.undrawn_greater_than_1_yr,
            collateral_1_value = obj.collateral_1_value,
            collateral_1_rating = obj.collateral_1_rating,
            collateral_1_residual_maturity = obj.collateral_1_residual_maturity,
            collateral_2_value = obj.collateral_2_value,
            collateral_2_rating = obj.collateral_2_rating,
            collateral_2_residual_maturity = obj.collateral_2_residual_maturity,
        )

        obj.delete()
        return True

    else:
        return False



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
def pd_report(account_no=None, start_date=None, end_date=None, s_type = 0, id_selected=None):

    #
    # Loading the data
    if s_type == 1:
        results = constants.TAB_ACTIVE["pd"][3].filter(account_no__isnull = False)
    else:
        results = constants.TAB_ACTIVE["pd"][4]

    #
    #
    if id_selected is None:

        if start_date is None and end_date is None and account_no is None:
            results = results.all()

        if start_date is not None:
            if end_date is not None:
                results = results.filter(date__gte = start_date, date__lte = end_date)
            else:
                results = results.filter(date__gte = start_date)

        if account_no is not None:
            results = results.filter(account_no__account_no__in = account_no)
    else:
        if s_type == 0:
            results = results.filter(id__in = id_selected)
            
    #
    #
    move_res = results
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
                pd_report.factor_1 = row["factor_1"]
                pd_report.factor_2 = row["factor_2"]
                pd_report.factor_3 = row["factor_3"]
                pd_report.factor_4 = row["factor_4"]
                pd_report.factor_5 = row["factor_5"]
                pd_report.factor_6 = row["factor_6"]
                pd_report.default_col = row["default_col"]
                pd_report.mgmt_overlay_1 = row["mgmt_overlay_1"]
                pd_report.mgmt_overlay_2 = row["mgmt_overlay_2"]
                pd_report.intercept = round(intercept[0],5)
                pd_report.coeff_fact1 = round(beta1[0],5)
                pd_report.coeff_fact2 = round(beta2[0],5)
                pd_report.coeff_fact3 = round(beta3[0],5)
                pd_report.coeff_fact4 = round(beta4[0],5)
                pd_report.zscore = round(row["zscore"],5)
                pd_report.pd = round(row["PD"],5)
                pd_report.save()

            except ObjectDoesNotExist:
                pd_report = PD_Report(
                    date = row["date"],
                    account_no = acc,
                    factor_1 = row["factor_1"],
                    factor_2 = row["factor_2"],
                    factor_3 = row["factor_3"],
                    factor_4 = row["factor_4"],
                    factor_5 = row["factor_5"],
                    factor_6 = row["factor_6"],
                    default_col = row["default_col"],
                    mgmt_overlay_1 = row["mgmt_overlay_1"],
                    mgmt_overlay_2 = row["mgmt_overlay_2"],
                    intercept = round(intercept[0],5),
                    coeff_fact1 = round(beta1[0],5),
                    coeff_fact2 = round(beta2[0],5),
                    coeff_fact3 = round(beta3[0],5),
                    coeff_fact4 = round(beta4[0],5),
                    zscore = round(row["zscore"],5),
                    pd = round(row["PD"],5)
                )

                pd_report.save()

        if s_type == 1:
            for row_mov in move_res:
                move_record("pd", row_mov)
        return True


# **********************************************************************
# LGD REPORT CALCULATION & DATA LOAD
# **********************************************************************
def lgd_report(account_no=None, start_date=None, end_date=None):

    #
    # Loading the data
    if s_type == 1:
        results = constants.TAB_ACTIVE["lgd"][3].filter(account_no__isnull = False)
    else:
        results = constants.TAB_ACTIVE["lgd"][4]

    if start_date is None and end_date is None and account_no is None:
        results = results.all()

    if start_date is not None:
        if end_date is not None:
            results = results.filter(date__gte = start_date, date__lte = end_date)
        else:
            results = results.filter(date__gte = start_date)

    if account_no is not None:
        results = results.filter(account_no__account_no__in = account_no)

    move_res = results
    results = results.select_related("account_no")

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

        if s_type == 1:
            for row_mov in move_res:
                move_record("lgd", row_mov)
        return True


# **********************************************************************
# STAGE REPORT CALCULATION & DATA LOAD
# **********************************************************************

def stage_report(account_no=None, start_date=None, end_date=None):

    #
    # Loading the data
    if s_type == 1:
        results = constants.TAB_ACTIVE["stage"][3].filter(account_no__isnull = False)
    else:
        results = constants.TAB_ACTIVE["stage"][4]

    if start_date is None and end_date is None and account_no is None:
        results = results.all()

    if start_date is not None:
        if end_date is not None:
            results = results.filter(date__gte = start_date, date__lte = end_date)
        else:
            results = results.filter(date__gte = start_date)

    if account_no is not None:
        results = results.filter(account_no__account_no__in = account_no)

    move_res = results
    results = results.select_related("account_no")

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

        if s_type == 1:
            for row_mov in move_res:
                move_record("stage", row_mov)
        return True



# **********************************************************************
# PD REPORT CALCULATION & DATA LOAD
# **********************************************************************
def ead_report(account_no=None, start_date=None, end_date=None):

    #
    # Loading the data
    if s_type == 1:
        results = constants.TAB_ACTIVE["ead"][3].filter(account_no__isnull = False)
    else:
        results = constants.TAB_ACTIVE["ead"][4]

    if start_date is None and end_date is None and account_no is None:
        results = results.all()

    if start_date is not None:
        if end_date is not None:
            results = results.filter(date__gte = start_date, date__lte = end_date)
        else:
            results = results.filter(date__gte = start_date)

    if account_no is not None:
        results = results.filter(account_no__account_no__in = account_no)

    move_res = results
    results = results.select_related("account_no")

    results = results.values('id', 'date', 'account_no_id', 'outstanding_amount', 'undrawn_upto_1_yr', 'undrawn_greater_than_1_yr', 'collateral_1_value', 'collateral_1_rating', 'collateral_1_residual_maturity', 'collateral_2_value', 'collateral_2_rating', 'collateral_2_residual_maturity', Account_No = F('account_no__account_no'), sectors = F('account_no__sectors'))

    if results.exists() is False:
        return False
    else:
        return True
