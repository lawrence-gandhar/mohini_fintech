#
# AUTHOR : LAWRENCE GANDHAR
# Project For Mohini - (India)
# Project Date : 21th Sept 2021
#

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.utils import timezone
from django.db import connection
from django.db.models import F
from django.conf import settings

from . import helpers
from . import constants
from . models import *

import json
import time

import pandas as pd
import numpy as np
import math
from sklearn.linear_model import LogisticRegression, LinearRegression
import os
from collections import defaultdict

import random


#**********************************************************************
# METHOD TO INSERT DATA INTO RELEVANT MODELS
#**********************************************************************
def insert_data(data_set, import_type, file_identifier=None):

    row_num = 0
    row_failed = 0
    total_rows = 0

    for row in data_set:
        total_rows += 1
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
            row_num += 1
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
            # BASEL COLLATERAL ENTRY
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
                    undrawn_greater_than_1_yr = helpers.clean_data(row["undrawn_greater_than_1_yr"]) if "undrawn_greater_than_1_yr" in col_names else None
                )

            #
            #
            if import_type == "ecl":
                ins = ECL_Initial.objects.create(
                    date = helpers.clean_data(row["date"]) if "date" in col_names else None,
                    tenure = helpers.clean_data(row["tenure"]) if "tenure" in col_names else None,
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
                row_num += 1
            except:
                row_failed += 1

    return row_num, row_failed, total_rows
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
         ins_const.ead_os = helpers.clean_data(row["ead_os"]) if "ead_os" in col_names else None
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
    # EAD
    if import_type == "ead":

        ins_const.date = helpers.clean_data(row["date"]) if "date" in col_names else None
        ins_const.outstanding_amount = helpers.clean_data(row["outstanding_amount"]) if "outstanding_amount" in col_names else None
        ins_const.undrawn_upto_1_yr = helpers.clean_data(row["undrawn_upto_1_yr"]) if "undrawn_upto_1_yr" in col_names else None
        ins_const.undrawn_greater_than_1_yr = helpers.clean_data(row["undrawn_greater_than_1_yr"]) if "undrawn_greater_than_1_yr" in col_names else None

    #
    # ECL
    if import_type == "ecl":

        ins_const.date = helpers.clean_data(row["date"]) if "date" in col_names else None
        ins_const.tenure = helpers.clean_data(row["tenure"]) if "tenure" in col_names else None

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
def move_record(request, tab_status=None, obj=None):

    created = None
    try:
        ins = constants.TAB_ACTIVE[tab_status][4].get(date = obj.date, account_no = obj.account_no)
    except ObjectDoesNotExist:
        ins = None

    if obj is None:
        return False

    if tab_status == "pd" and obj is not None:

        if ins is None:
            created = constants.TAB_ACTIVE[tab_status][4].create(
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
        else:
            ins.date = obj.date
            ins.account_no = obj.account_no
            ins.factor_1 = obj.factor_1
            ins.factor_2 = obj.factor_2
            ins.factor_3 = obj.factor_3
            ins.factor_4 = obj.factor_4
            ins.factor_5 = obj.factor_5
            ins.factor_6 = obj.factor_6
            ins.default_col = obj.default_col
            ins.mgmt_overlay_1 = obj.mgmt_overlay_1
            ins.mgmt_overlay_2 = obj.mgmt_overlay_2
            ins.save()

    elif tab_status == "lgd" and obj is not None:
        if ins is None:
            created = constants.TAB_ACTIVE[tab_status][4].create(
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
        else:
            ins.date = obj.date,
            ins.account_no = obj.account_no
            ins.ead_os = obj.ead_os
            ins.pv_cashflows = obj.pv_cashflows
            ins.pv_cost = obj.pv_cost
            ins.beta_value = obj.beta_value
            ins.sec_flag = obj.sec_flag
            ins.factor_4 = obj.factor_4
            ins.factor_5 = obj.factor_5
            ins.avg_1 = obj.avg_1
            ins.avg_2 = obj.avg_2
            ins.avg_3 = obj.avg_3
            ins.avg_4 = obj.avg_4
            ins.avg_5 = obj.avg_5
            ins.mgmt_overlay_1 = obj.mgmt_overlay_1
            ins.mgmt_overlay_2 = obj.mgmt_overlay_2
            ins.save()

    elif tab_status == "stage" and obj is not None:
        if ins is None:
            created = constants.TAB_ACTIVE[tab_status][4].create(
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
        else:
            ins.date = obj.date
            ins.account_no = obj.account_no
            ins.old_rating = obj.old_rating
            ins.new_rating = obj.new_rating
            ins.rating_3 = obj.rating_3
            ins.rating_4 = obj.rating_4
            ins.rating_5 = obj.rating_5
            ins.rating_6 = obj.rating_6
            ins.rating_7 = obj.rating_7
            ins.day_bucket_1 = obj.day_bucket_1
            ins.day_bucket_2 = obj.day_bucket_2
            ins.day_bucket_3 = obj.day_bucket_3
            ins.day_bucket_4 = obj.day_bucket_4
            ins.day_bucket_5 = obj.day_bucket_5
            ins.day_bucket_6 = obj.day_bucket_6
            ins.day_bucket_7 = obj.day_bucket_7
            ins.day_bucket_8 = obj.day_bucket_8
            ins.day_bucket_9 = obj.day_bucket_9
            ins.day_bucket_10 = obj.day_bucket_10
            ins.day_bucket_11 = obj.day_bucket_11
            ins.day_bucket_12 = obj.day_bucket_12
            ins.day_bucket_13 = obj.day_bucket_13
            ins.day_bucket_14 = obj.day_bucket_14
            ins.day_bucket_15 = obj.day_bucket_15
            ins.criteria = obj.criteria
            ins.cooling_period_1 = obj.cooling_period_1
            ins.cooling_period_2 = obj.cooling_period_2
            ins.cooling_period_3 = obj.cooling_period_3
            ins.cooling_period_4 = obj.cooling_period_4
            ins.cooling_period_5 = obj.cooling_period_5
            ins.rbi_window = obj.rbi_window
            ins.mgmt_overlay_1 = obj.mgmt_overlay_1
            ins.mgmt_overlay_2 = obj.mgmt_overlay_2
            ins.save()

    elif tab_status == "ead" and obj is not None:

        if ins is None:
            created = constants.TAB_ACTIVE[tab_status][4].create(
                date = obj.ead_date,
                account_no = obj.account_no,
                outstanding_amount = obj.outstanding_amount,
                undrawn_upto_1_yr = obj.undrawn_upto_1_yr,
                undrawn_greater_than_1_yr = obj.undrawn_greater_than_1_yr
            )
        else:
            ins.date = obj.ead_date
            ins.account_no = obj.account_no
            ins.outstanding_amount = obj.outstanding_amount
            ins.undrawn_upto_1_yr = obj.undrawn_upto_1_yr
            ins.undrawn_greater_than_1_yr = obj.undrawn_greater_than_1_yr
            ins.save()


    elif tab_status == "ecl" and obj is not None:
        if ins is None:
            created = constants.TAB_ACTIVE[tab_status][4].create(
                date = obj.date,
                account_no = obj.account_no,
                tenure = obj.tenure,
            )
        else:
            ins.date = obj.date
            ins.account_no = obj.account_no
            ins.tenure = obj.tenure
            ins.save()

    #
    # Audit Trail
    helpers.audit_trail(request, {
        "parent" : tab_status,
        "moved_data" : True,
        "params":{"handler_table": "initial", "selected_ids":[obj.id], "created_ids":[created.id if created is not None else ins.id], "all":False}
    })

    obj.delete()
    return True



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

        selected_ids = []
        created_ids = []

        #
        # Queryset
        qry = constants.TAB_ACTIVE[tab_status][3].filter(account_no__isnull = False)

        #
        # Total Records
        records_total = constants.TAB_ACTIVE[tab_status][3].count()

        #
        # Valid Records found for movement
        records_valid = qry.count()

        # Create Insert statement for each tab_status
        if tab_status == "pd":
            result_set = qry.values_list('id', 'date', 'account_no', 'factor_1', 'factor_2', 'factor_3', 'factor_4', 'factor_5', 'factor_6', 'default_col', 'mgmt_overlay_1', 'mgmt_overlay_2')

        if tab_status == "lgd":
            result_set = qry.values_list('id', 'date', 'account_no', 'ead_os', 'pv_cashflows', 'pv_cost', 'beta_value', 'sec_flag', 'factor_4', 'factor_5', 'avg_1', 'avg_2', 'avg_3', 'avg_4', 'avg_5', 'mgmt_overlay_1', 'mgmt_overlay_2')

        if tab_status == "stage":
            result_set = qry.values_list('id', 'date', 'account_no', 'old_rating', 'new_rating', 'rating_3', 'rating_4', 'rating_5', 'rating_6', 'rating_7', 'day_bucket_1', 'day_bucket_2', 'day_bucket_3', 'day_bucket_4', 'day_bucket_5', 'day_bucket_6', 'day_bucket_7', 'day_bucket_8', 'day_bucket_9', 'day_bucket_10', 'day_bucket_11', 'day_bucket_12','day_bucket_13', 'day_bucket_14', 'day_bucket_15', 'criteria', 'cooling_period_1', 'cooling_period_2', 'cooling_period_3', 'cooling_period_4', 'cooling_period_5', 'rbi_window', 'mgmt_overlay_1', 'mgmt_overlay_2')

        if tab_status == "ead":
            result_set = qry.values_list('id', 'date', 'account_no', 'outstanding_amount', 'undrawn_upto_1_yr', 'undrawn_greater_than_1_yr')

        if tab_status == "ecl":
            result_set = qry.values_list('id', 'date', 'account_no', 'tenure')

        #
        # If valid records found : then capture & iterate to insert
        if records_valid > 0:


            #
            # Iterate over each row & insert
            for row in result_set:

                # Create Insert/Update statement for each tab_status
                if tab_status == "pd":
                    insert_qry = """
                        insert into {0} (date, account_no_id, factor_1, factor_2, factor_3, factor_4, factor_5, factor_6, default_col, mgmt_overlay_1, mgmt_overlay_2, created_on)""".format(constants.TAB_ACTIVE[tab_status][6])

                    update_qry = """
                        update {0} set factor_1='{3}', factor_2='{4}', factor_3='{5}', factor_4='{6}', factor_5='{7}', factor_6='{8}', default_col='{9}', mgmt_overlay_1='{10}', mgmt_overlay_2='{11}', created_on='{12}' where date='{1}' and account_no_id='{2}'
                        """

                if tab_status == "lgd":
                    insert_qry = """
                        insert into {0} (date, account_no_id, ead_os, pv_cashflows, pv_cost, beta_value, sec_flag, factor_4, factor_5, avg_1, avg_2, avg_3, avg_4, avg_5, mgmt_overlay_1, mgmt_overlay_2, created_on)""".format(constants.TAB_ACTIVE[tab_status][6])

                    update_qry = """
                        update {0} set ead_os='{3}', pv_cashflows='{4}', pv_cost='{5}', beta_value='{6}', sec_flag='{7}', factor_4='{8}', factor_5='{9}', avg_1='{10}', avg_2='{11}', avg_3='{12}', avg_4='{13}', avg_5='{14}', mgmt_overlay_1='{15}', mgmt_overlay_2='{16}', created_on='{17}' where date='{1}' and account_no_id='{2}'
                        """

                if tab_status == "stage":
                    insert_qry = """
                        insert into {0} (date, account_no_id, old_rating, new_rating, rating_3, rating_4, rating_5, rating_6, rating_7, day_bucket_1, day_bucket_2, day_bucket_3, day_bucket_4, day_bucket_5, day_bucket_6, day_bucket_7, day_bucket_8, day_bucket_9, day_bucket_10, day_bucket_11, day_bucket_12, day_bucket_13, day_bucket_14, day_bucket_15, criteria, cooling_period_1, cooling_period_2, cooling_period_3, cooling_period_4, cooling_period_5, rbi_window, mgmt_overlay_1, mgmt_overlay_2, created_on)""".format(constants.TAB_ACTIVE[tab_status][6])

                    update_qry = """
                        update {0} set old_rating='{3}', new_rating='{4}', rating_3='{5}', rating_4='{6}', rating_5='{7}', rating_6='{8}', rating_7='{9}', day_bucket_1='{10}', day_bucket_2='{11}', day_bucket_3='{12}', day_bucket_4='{13}', day_bucket_5='{14}', day_bucket_6='{15}', day_bucket_7='{16}', day_bucket_8='{17}', day_bucket_9='{18}', day_bucket_10='{19}', day_bucket_11='{20}', day_bucket_12='{21}', day_bucket_13='{22}', day_bucket_14='{23}', day_bucket_15='{24}', criteria='{25}', cooling_period_1='{26}', cooling_period_2='{27}', cooling_period_3='{28}', cooling_period_4='{29}', cooling_period_5='{30}', rbi_window='{31}', mgmt_overlay_1='{32}', mgmt_overlay_2='{33}', created_on='{34}' where date='{1}' and account_no_id='{2}'
                    """

                if tab_status == "ead":
                    insert_qry = """
                        insert into {0} (date, account_no_id, outstanding_amount, undrawn_upto_1_yr, undrawn_greater_than_1_yr, created_on)""".format(constants.TAB_ACTIVE[tab_status][6])

                    update_qry = """
                        update {0} set outstanding_amount='{3}', undrawn_upto_1_yr='{4}', undrawn_greater_than_1_yr='{5}', created_on='{6}' where date='{1}' and account_no_id='{2}'
                    """

                if tab_status == "ecl":
                    insert_qry = """
                        insert into {0} (date, account_no_id, tenure, created_on)""".format(constants.TAB_ACTIVE[tab_status][6])

                    update_qry = """
                        update {0} set tenure='{3}', created_on='{6}' where date='{1}' and account_no_id='{2}'
                    """


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

                            selected_ids.append(row_id)
                            created_ids.append(ins.id)

                            constants.TAB_ACTIVE[tab_status][3].get(pk = row_id).delete()

                except:
                    constants.TAB_ACTIVE[tab_status][4].filter(date = row[0], account_no_id = row[1]).delete()

                    #
                    # Insert record
                    with connection.cursor() as cursor:

                        formatted_data = [x if x is not None else '' for x in row]
                        formatted_data.append(timezone.now())

                        value_params = "'{}', "*(len(formatted_data))
                        value_params = value_params.rstrip(', ')

                        main_query = insert_qry+"values({})".format(value_params)
                        main_query = main_query.format(*formatted_data)

                        print(main_query)

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
                            latest = constants.TAB_ACTIVE[tab_status][4].latest('id')

                            selected_ids.append(row_id)
                            created_ids.append(latest.id)

                            constants.TAB_ACTIVE[tab_status][3].get(pk = row_id).delete()

        else:
            msg = "No valid rows to move"


    if records_moved >0 :
        msg = "Records Moved Successfully"
        ret = True

        #
        # Audit Trail
        helpers.audit_trail(request, {
            "parent" : tab_status,
            "moved_data" : True,
            "params":{"handler_table": "initial", "selected_ids":list(set(selected_ids)), "created_ids":list(set(created_ids)), "all":True}
        })

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
def pd_report(request, account_no=None, start_date=None, end_date=None, s_type = 0, id_selected=None):

    #
    # Loading the data
    #=============================================================
    if s_type == 1:
        results = constants.TAB_ACTIVE["pd"][3].filter(account_no__isnull = False)

        params = {
            "parent" : "pd",
            "report_run" : True,
            "params":{"handler_table": "initial", "start_date":start_date, "end_date":end_date, "account_no":account_no, "selected_ids":id_selected, "all":False}
        }

    else:
        results = constants.TAB_ACTIVE["pd"][4]

        params = {
            "parent" : "pd",
            "report_run" : True,
            "params":{"handler_table": "final", "start_date":start_date, "end_date":end_date, "account_no":account_no, "selected_ids":id_selected, "all":False}
        }

    #
    #
    #=============================================================
    if id_selected is None or len(id_selected) == 0:

        if start_date is None and end_date is None and account_no is None:
            results = results.all()
            params["params"]["all"] = True

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
    # Audit Trail
    #=============================================================
    helpers.audit_trail(request, params)


    #
    #
    #=============================================================
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
                pd_report.factor_1 = round(row["factor_1"], 5) if row["factor_1"] is not None and row["factor_1"] !="" else None
                pd_report.factor_2 = round(row["factor_2"], 5) if row["factor_2"] is not None and row["factor_2"] !="" else None
                pd_report.factor_3 = round(row["factor_3"], 5) if row["factor_3"] is not None and row["factor_3"] !="" else None
                pd_report.factor_4 = round(row["factor_4"], 5) if row["factor_4"] is not None and row["factor_4"] !="" else None
                pd_report.factor_5 = round(row["factor_5"], 5) if row["factor_5"] is not None and row["factor_5"] !="" else None
                pd_report.factor_6 = round(row["factor_6"], 5) if row["factor_6"] is not None and row["factor_6"] !="" else None
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
                pd_report = PD_Report.objects.create(
                    date = row["date"],
                    account_no = acc,
                    factor_1 = round(row["factor_1"], 5) if row["factor_1"] is not None and row["factor_1"] !="" else None,
                    factor_2 = round(row["factor_2"], 5) if row["factor_2"] is not None and row["factor_2"] !="" else None,
                    factor_3 = round(row["factor_3"], 5) if row["factor_3"] is not None and row["factor_3"] !="" else None,
                    factor_4 = round(row["factor_4"], 5) if row["factor_4"] is not None and row["factor_4"] !="" else None,
                    factor_5 = round(row["factor_5"], 5) if row["factor_5"] is not None and row["factor_5"] !="" else None,
                    factor_6 = round(row["factor_6"], 5) if row["factor_6"] is not None and row["factor_6"] !="" else None,
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

        if s_type == 1:
            for row_mov in move_res:
                move_record(request, "pd", row_mov)

        return True


# **********************************************************************
# LGD REPORT CALCULATION & DATA LOAD
# **********************************************************************
def lgd_report(request, account_no=None, start_date=None, end_date=None, s_type = 0, id_selected=None):

    #
    # Loading the data
    #=============================================================
    if s_type == 1:
        results = constants.TAB_ACTIVE["lgd"][3].filter(account_no__isnull = False)

        params = {
            "parent" : "lgd",
            "report_run" : True,
            "params":{"handler_table": "initial", "start_date":start_date, "end_date":end_date, "account_no":account_no, "selected_ids":id_selected, "all":False}
        }

    else:
        results = constants.TAB_ACTIVE["lgd"][4]

        params = {
            "parent" : "lgd",
            "report_run" : True,
            "params":{"handler_table": "final", "start_date":start_date, "end_date":end_date, "account_no":account_no, "selected_ids":id_selected, "all":False}
        }


    #
    #
    #=============================================================
    if id_selected is None or len(id_selected) == 0:

        if start_date is None and end_date is None and account_no is None:
            results = results.all()
            params["params"]["all"] = True

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
    # Audit Trail
    #=============================================================
    helpers.audit_trail(request, params)


    #
    #
    #=============================================================
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
        rows = Output_LGD.to_dict('index')

        #print(rows)

        for idx, row in rows.items():

            try:
                acc = AccountMaster.objects.get(pk = int(row["account_no_id"]))
            except ObjectDoesNotExist:
                return False

            try:
                lgd_report = LGD_Report.objects.get(date = row["date"], account_no = acc)

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
                lgd_report.rec_rate = round(row["rec_rate"], 5)
                lgd_report.est_rr = round(row["est_rr"], 5)
                lgd_report.est_lgd = round(row["est_lgd"], 5)
                lgd_report.final_lgd = round(row["lgd"], 5)
                lgd_report.save()

            except ObjectDoesNotExist:
                lgd_report = LGD_Report(
                    date = row["date"],
                    account_no = acc,
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
                    rec_rate = round(row["rec_rate"], 5),
                    est_rr = round(row["est_rr"], 5),
                    est_lgd = round(row["est_lgd"], 5),
                    final_lgd = round(row["lgd"], 5)
                )

                lgd_report.save()

        if s_type == 1:
            for row_mov in move_res:
                move_record(request, "lgd", row_mov)
        return True


# **********************************************************************
# STAGE REPORT CALCULATION & DATA LOAD
# **********************************************************************

def stage_report(request, account_no=None, start_date=None, end_date=None, s_type = 0, id_selected=None):

    #
    # Loading the data
    #=============================================================
    if s_type == 1:
        results = constants.TAB_ACTIVE["stage"][3].filter(account_no__isnull = False)

        params = {
            "parent" : "stage",
            "report_run" : True,
            "params":{"handler_table": "initial", "start_date":start_date, "end_date":end_date, "account_no":account_no, "selected_ids":id_selected, "all":False}
        }

    else:
        results = constants.TAB_ACTIVE["stage"][4]

        params = {
            "parent" : "stage",
            "report_run" : True,
            "params":{"handler_table": "final", "start_date":start_date, "end_date":end_date, "account_no":account_no, "selected_ids":id_selected, "all":False}
        }


    #
    #
    #=============================================================
    if id_selected is None or len(id_selected) == 0:

        if start_date is None and end_date is None and account_no is None:
            results = results.all()
            params["params"]["all"] = True

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
    # Audit Trail
    #=============================================================
    helpers.audit_trail(request, params)

    move_res = results
    results = results.select_related("account_no")


    results = results.values('id', 'date', 'account_no_id', 'old_rating', 'new_rating', 'rating_3', 'rating_4', 'rating_5', 'rating_6', 'rating_7', 'day_bucket_1', 'day_bucket_2', 'day_bucket_3', 'day_bucket_4', 'day_bucket_5', 'day_bucket_6', 'day_bucket_7', 'day_bucket_8', 'day_bucket_9', 'day_bucket_10', 'day_bucket_11', 'day_bucket_12','day_bucket_13', 'day_bucket_14', 'day_bucket_15', 'criteria', 'cooling_period_1', 'cooling_period_2', 'cooling_period_3', 'cooling_period_4', 'cooling_period_5', 'rbi_window', 'mgmt_overlay_1', 'mgmt_overlay_2', Account_No = F('account_no__account_no'), sectors = F('account_no__sectors'))

    if results.exists() is False:
        return False
    else:

        df = pd.DataFrame(results)
        df = df.set_index('id')

        df["state"] = "No Change"
        df["stage"] = "1"

        ssd = df.index.tolist()

        for i in ssd:
            if ((df["old_rating"][i]=="BBB") and (df["new_rating"][i]=="BB")):
                df["state"][i]="Downgrade"
            if ((df["old_rating"][i]=="BB") and (df["new_rating"][i]=="B")):
                df["state"][i]="Downgrade"
            if ((df["old_rating"][i]=="C") and (df["new_rating"][i]=="D")):
                df["state"][i]="Default"
            if ((df["old_rating"][i]=="D") and (df["new_rating"][i]=="D")):
                df["state"][i]="Default"
            if (df["state"][i]=="Downgrade"):
                df["stage"][i]="2"
            if (df["state"][i]=="Default"):
                df["stage"][i]="3"

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
                move_record(request, "stage", row_mov)
        return True



# **********************************************************************
# PD REPORT CALCULATION & DATA LOAD
# **********************************************************************

def ead_report(request, account_no=None, start_date=None, end_date=None, s_type = 0, id_selected=None):

    #
    # Loading the data

    where_clause = False
    dates_cond = ""
    acc_cond = ""

    params = {
        "parent" : "ead",
        "report_run" : True,
        "params":{"handler_table": "initial", "start_date":start_date, "end_date":end_date, "account_no":account_no, "selected_ids":[], "all":False}
    }

    #
    #=============================================================
    if id_selected is None or len(id_selected) == 0:

        params["params"]["all"] = True

        if start_date is None and end_date is None and account_no is None:
            dates_cond = ""
        else:
            if start_date is not None:
                if end_date is not None:
                    dates_cond = " where ED.date >='{}' and ED.date <='{}'".format(start_date, end_date)
                    where_clause = True
                else:
                    dates_cond = " where ED.date >='{}'".format(start_date)
                    where_clause = True

        if account_no is not None:
            if where_clause:
                acc_cond = " and ED.account_no_id = {}".format(account_no)
            else:
                acc_cond = " where ED.account_no_id = {}".format(account_no)
    else:
        acc_cond = " where ED.id in ({})".format(','.join(id_selected))

    #
    #
    #
    if s_type == 1:
        qry = """select BP.product_name, BP.product_code, AC.account_no as Account_no, AC.cin, AC.sectors, AC.account_type, ED.id as id, C1.collateral_value, C1.collateral_rating, C1.collateral_residual_maturity, ED.outstanding_amount, ED.undrawn_upto_1_yr, ED.date as ead_date, ED.undrawn_greater_than_1_yr,  ED.account_no_id, C1.id as collateral_id, BC.basel_collateral_code, BC.collateral_rating as b_col_rating, BP.drawn_cff, BP.cff_upto_1_yr, BP.cff_gt_1_yr, BC.issuer_type, BC.collateral_code as c_code, BC.collateral_type, BC.collateral_eligibity, BC.rating_available, BC.residual_maturity, BC.basel_collateral_type, BC.basel_collateral_subtype, BC.basel_collateral_rating, BC.soverign_issuer, BC.other_issuer
        from app_ead_initial ED
        left join app_collateral C1 on C1.account_no_id = ED.account_no_id
		inner join app_accountmaster AC on ED.account_no_id = AC.id
        left join app_basel_product_master BP on C1.product_id = BP.id
        left join app_basel_collateral_master BC on C1.collateral_code_id = BC.id {} {} and ED.account_no_id is not null order by ED.id
        """.format(dates_cond, acc_cond)

        qs = constants.TAB_ACTIVE["ead"][3].raw(qry)
        params["params"]["handler_table"] =  "initial"


    else:
        qry = """select BP.product_name, BP.product_code, AC.account_no as Account_no, AC.cin, AC.sectors, AC.account_type, ED.id as id, C1.collateral_value, C1.collateral_rating, C1.collateral_residual_maturity, ED.outstanding_amount, ED.undrawn_upto_1_yr, ED.date as ead_date, ED.undrawn_greater_than_1_yr,  ED.account_no_id, C1.id as collateral_id, BC.basel_collateral_code, BC.collateral_rating as b_col_rating, BP.drawn_cff, BP.cff_upto_1_yr, BP.cff_gt_1_yr, BC.issuer_type, BC.collateral_code as c_code, BC.collateral_type, BC.collateral_eligibity, BC.rating_available, BC.residual_maturity, BC.basel_collateral_type, BC.basel_collateral_subtype, BC.basel_collateral_rating, BC.soverign_issuer, BC.other_issuer
        from app_ead_final ED
        left join app_collateral C1 on C1.account_no_id = ED.account_no_id
		inner join app_accountmaster AC on ED.account_no_id = AC.id
        left join app_basel_product_master BP on C1.product_id = BP.id
        left join app_basel_collateral_master BC on C1.collateral_code_id = BC.id {} {}
        order by id
        """.format(dates_cond, acc_cond)

        qs = constants.TAB_ACTIVE["ead"][4].raw(qry)
        params["params"]["handler_table"] =  "final"


    #
    # Audit Trail
    #=============================================================
    helpers.audit_trail(request, params)


    #
    #
    cus_dict = defaultdict()

    for row in qs:
        cus_dict[row.id] = {
            "ead_date":row.ead_date,
            "account_no":row.Account_no,
            "account_no_id":row.account_no_id,
            "outstanding_amount":row.outstanding_amount,
            "undrawn_upto_1_yr":row.undrawn_upto_1_yr,
            "undrawn_greater_than_1_yr":row.undrawn_greater_than_1_yr,
            "drawn_cff":row.drawn_cff,
            "cff_upto_1_yr":row.cff_upto_1_yr,
            "cff_gt_1_yr":row.cff_gt_1_yr,
            "collaterals":[],
            "ead_total":0,
        }

    for row in qs:

        b_col_rating = row.b_col_rating if row.b_col_rating is not None else "-"
        col_rating = row.collateral_rating if row.collateral_rating is not None else "-"

        cus_dict[row.id]["collaterals"].append({
            "basel_collateral_code":row.basel_collateral_code,
            "collateral_value":row.collateral_value,
            "issuer_type":row.issuer_type,
            "soverign_issuer":row.soverign_issuer,
            "other_issuer":row.other_issuer,
        })


    #
    #
    for key, row in cus_dict.items():
        drawn_cff = 1.0
        cff_upto_1_yr = 1.0
        cff_gt_1_yr = 1.0
        ead_total = 0

        try:
            drawn_cff = (float(row["drawn_cff"].replace("%", ""))/100)
            ead_total += float(row["outstanding_amount"]) * drawn_cff
        except:
            ead_total += drawn_cff * (float(row["outstanding_amount"]) if row["outstanding_amount"] !="" and row["outstanding_amount"] is not None else 0)

        try:
            cff_upto_1_yr = (float(row["cff_upto_1_yr"].replace("%", ""))/100)
            ead_total += float(row["undrawn_upto_1_yr"]) * cff_upto_1_yr
        except:
            ead_total += cff_upto_1_yr * (float(row["undrawn_upto_1_yr"]) if row["undrawn_upto_1_yr"] !="" and row["undrawn_upto_1_yr"] is not None else 0)

        try:
            cff_gt_1_yr = (float(row["cff_gt_1_yr"].replace("%", ""))/100)
            ead_total += float(row["undrawn_greater_than_1_yr"]) * cff_gt_1_yr
        except:
            ead_total += cff_gt_1_yr * (float(row["undrawn_greater_than_1_yr"]) if row["undrawn_greater_than_1_yr"] !="" and row["undrawn_greater_than_1_yr"] is not None else 0)


        # if collteral found
        #

        total_coll = 0

        for coll in row["collaterals"]:
            if coll["basel_collateral_code"] is not None:

                if coll["issuer_type"] == "1":
                    try:
                        total_coll += float(coll["collateral_value"]) * (1 - float(coll["soverign_issuer"])/100)
                    except:
                        pass
                else:
                    try:
                        total_coll += float(coll["collateral_value"]) * (1 - float(coll["other_issuer"])/100)
                    except:
                        pass

        cus_dict[key]["ead_total"] = ead_total - total_coll

        #
        # Load data into Report Table
        try:
            acc = AccountMaster.objects.get(pk = int(row["account_no_id"]))
        except:
            acc = None

        if acc is not None:
            try:
                # Edit
                ead_report = EAD_Report.objects.get(date = row["ead_date"], account_no = acc)
                ead_report.outstanding_amount = row["outstanding_amount"]
                ead_report.undrawn_upto_1_yr = row["undrawn_upto_1_yr"]
                ead_report.undrawn_greater_than_1_yr = row["undrawn_greater_than_1_yr"]
                ead_report.ead_total = round(row["ead_total"],2)
                ead_report.save()
            except:
                EAD_Report.objects.create(
                    date = row["ead_date"],
                    account_no = acc,
                    outstanding_amount = row["outstanding_amount"],
                    undrawn_upto_1_yr = row["undrawn_upto_1_yr"],
                    undrawn_greater_than_1_yr = row["undrawn_greater_than_1_yr"],
                    ead_total = round(row["ead_total"],2)
                )

    if s_type == 1:
        for row_mov in qs:
            move_record(request, "ead", row_mov)
    return True


# **********************************************************************
# STAGE REPORT CALCULATION & DATA LOAD
# **********************************************************************

def ecl_report(request, account_no=None, start_date=None, end_date=None, s_type = 0, id_selected=None):

    #
    # Loading the data

    where_clause = False
    dates_cond = ""
    acc_cond = ""

    params = {
        "parent" : "ecl",
        "report_run" : True,
        "params":{"handler_table": "initial", "start_date":start_date, "end_date":end_date, "account_no":account_no, "selected_ids":[], "all":False}
    }

    #
    #=============================================================
    if id_selected is None or len(id_selected) == 0:

        params["params"]["all"] = True

        if start_date is None and end_date is None and account_no is None:
            dates_cond = ""
        else:
            if start_date is not None:
                if end_date is not None:
                    dates_cond = " where ECL.date >='{}' and ECL.date <='{}'".format(start_date, end_date)
                    where_clause = True
                else:
                    dates_cond = " where ECL.date >='{}'".format(start_date)
                    where_clause = True

        if account_no is not None:
            if where_clause:
                acc_cond = " and ECL.account_no_id = {}".format(account_no)
            else:
                acc_cond = " where ECL.account_no_id = {}".format(account_no)
    else:
        acc_cond = " where ECL.id in ({})".format(','.join(id_selected))

    #
    #
    #
    if s_type == 1:
        qry = """select BP.product_name, BP.product_code, AC.account_no as Account_no, AC.cin, AC.sectors, AC.account_type, ECL.id as id, ECL.tenure, PD.pd, LGD.final_lgd, ST.stage, EAD.ead_total, ECL.account_no_id
        from app_ecl_initial ECL
        left join (select * from app_collateral group by account_no_id) C1 on ECL.account_no_id = C1.account_no_id
		left join app_accountmaster AC on ECL.account_no_id = AC.id
        left join app_basel_product_master BP on C1.product_id = BP.id
        left join app_pd_report PD on PD.account_no_id = ECL.account_no_id and PD.date = ECL.date
        left join app_lgd_report LGD on LGD.account_no_id = ECL.account_no_id and LGD.date = ECL.date
        left join app_stage_report ST on ST.account_no_id = ECL.account_no_id and ST.date = ECL.date
        left join app_ead_report EAD on EAD.account_no_id = ECL.account_no_id and EAD.date = ECL.date
        {} {} and ECL.account_no_id is not null order by ECL.id
        """.format(dates_cond, acc_cond)

        qs = constants.TAB_ACTIVE["ecl"][4].raw(qry)


    else:
        qry = """select BP.product_name, BP.product_code, AC.account_no as Account_no, AC.cin, AC.sectors, AC.account_type, ECL.id as id, ECL.tenure, PD.pd, LGD.final_lgd, ST.stage, EAD.ead_total, ECL.account_no_id
        from app_ecl_final ECL
        left join (select * from app_collateral group by account_no_id) C1 on ECL.account_no_id = C1.account_no_id
		left join app_accountmaster AC on ECL.account_no_id = AC.id
        left join app_basel_product_master BP on C1.product_id = BP.id
        left join app_pd_report PD on PD.account_no_id = ECL.account_no_id and PD.date = ECL.date
        left join app_lgd_report LGD on LGD.account_no_id = ECL.account_no_id and LGD.date = ECL.date
        left join app_stage_report ST on ST.account_no_id = ECL.account_no_id and ST.date = ECL.date
        left join app_ead_report EAD on EAD.account_no_id = ECL.account_no_id and EAD.date = ECL.date {} {}
        order by ECL.id
        """.format(dates_cond, acc_cond)

        qs = constants.TAB_ACTIVE["ecl"][4].raw(qry)

        params["params"]["handler_table"] =  "final"

    #
    # Audit Trail
    #=============================================================
    helpers.audit_trail(request, params)

    #
    #=============================================================
    for row in qs:

        #
        # Load data into Report Table
        try:
            acc = AccountMaster.objects.get(pk = int(row.account_no_id))
        except:
            return False

        PD = float(row.pd) if row.pd is not None and row.pd !="" else 1
        LGD = float(row.final_lgd) if row.final_lgd is not None and row.final_lgd !="" else 1
        EAD = float(row.ead_total) if row.ead_total is not None and row.ead_total !="" else 1
        EIR = random.random() * 10
        Tenure = float(row.tenure) if row.tenure is not None and row.tenure !="" else 1

        #
        #

        final_ecl = 0
        if row.stage == "1":
            final_ecl = round(PD * LGD * EAD, 5)
        elif row.stage == "2":
            final_ecl = round((PD * LGD * EAD)/(1+EIR) ** Tenure, 5)
        elif row.stage == "3":
            final_ecl = round((1 * LGD * EAD)/(1+EIR) ** Tenure, 5)

        try:
            # Edit
            ecl_report = ECL_Reports.objects.get(date = row.date, account_no = acc)
            ecl_report.tenure = row.tenure
            ecl_report.final_ecl = final_ecl
            ecl_report.eir = "{}%".format(round(EIR,2))
            ecl_report.save()
        except:
            ECL_Reports.objects.create(
                date = row.date,
                account_no = acc,
                tenure = row.tenure,
                eir = "{}%".format(round(EIR,2)),
                final_ecl = final_ecl
            )

    if s_type == 1:
        for row_mov in qs:
            move_record(request, "ecl", row_mov)
    return True



# **********************************************************************
# DOWNLOAD REPORTS
# **********************************************************************

def download_reports(tab_status=None, start_date=None, end_date=None, ftype=0):

    results = constants.TAB_ACTIVE[tab_status][9]

    if start_date is not None:
        results = results.filter(date__gte = start_date)

        if end_date is not None:
            results = results.filter(date__lte = end_date)


    if tab_status == "pd":
        product_qry = """select product_name from app_basel_product_master where id = (select distinct(product_id) from app_collateral where account_no_id = app_pd_report.account_no_id)"""

        results = results.extra(select={'product_name': product_qry}).select_related('account_no').values('id', 'date', 'account_no__account_no', 'account_no__cin', 'account_no__account_type', 'account_no__sectors', 'product_name', 'factor_1', 'factor_2', 'factor_3', 'factor_4', 'factor_5', 'factor_6', 'default_col', 'mgmt_overlay_1', 'mgmt_overlay_2', 'intercept', 'coeff_fact1', 'coeff_fact2', 'coeff_fact3', 'coeff_fact4', 'zscore', 'pd')

    if tab_status == "lgd":
        product_qry = """select product_name from app_basel_product_master where id = (select distinct(product_id) from app_collateral where account_no_id = app_lgd_report.account_no_id)"""

        results = results.extra(select={'product_name': product_qry}).select_related('account_no').values('id', 'date', 'account_no__account_no', 'account_no__cin', 'account_no__account_type', 'account_no__sectors', 'product_name', 'ead_os', 'pv_cashflows', 'pv_cost', 'beta_value', 'factor_5', 'sec_flag', 'factor_4', 'factor_5', 'avg_1', 'avg_2', 'avg_3', 'avg_4', 'avg_5', 'mgmt_overlay_2', 'rec_rate', 'est_rr', 'est_lgd', 'final_lgd')

    df = pd.DataFrame(results)
    df = df.set_index('id')

    df.rename({'account_no__account_no':'account_no', 'account_no__cin':'cin', 'account_no__account_type':'account_type', 'account_no__sectors':'sectors'}, axis=1, inplace=True)

    if ftype == 0:
        file_name = os.path.join(settings.REPORTS_DIR, "output.xlsx")
        df.to_excel(file_name, sheet_name='Sheet_name_1', float_format='%.5f', index=False)
        return file_name
    else:
        return df
