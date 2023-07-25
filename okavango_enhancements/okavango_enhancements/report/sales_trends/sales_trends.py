# Copyright (c) 2023, Bantoo and contributors
# For license information, please see license.txt

import frappe
from erpnext.controllers.trends import *


def execute(filters=None):
    if not filters:
        filters = {}
    data = []
    conditions = get_columns(filters, "Sales Invoice")
    data = get_data_with_bundle_breakdown(filters, conditions)
    

    return conditions["columns"], data

def is_product_bundle(item_name):
    return frappe.db.exists("Product Bundle", item_name)

def break_down_bundle(item_name):
    bundle_doc = frappe.get_doc("Product Bundle", item_name)
    items = []


    for bundle_item in bundle_doc.items:
        rate = frappe.db.get_value('Item', bundle_item.item_code, 'standard_rate')
        amount = bundle_item.qty * rate
        items.append([bundle_item.item_code, bundle_item.item_code, bundle_item.qty, amount, bundle_item.qty, amount])
        
    return items

def print(text):
    #return
    frappe.errprint(text)

def get_data_with_bundle_breakdown(filters, conditions):
    raw_data = get_data(filters, conditions)
    new_data = []
    item_dict = {}

    period = filters.get("period")
    unbundle_items = filters.get("unbundle_items")
    based_on = filters.get("based_on")

    if unbundle_items != 1 or based_on != "Item":
        return raw_data

    if period == "Yearly":
        for row in raw_data:
            item_name = row[1] # select the item_name from the row

            # only debug items
            if not item_name.startswith("Nice") and not item_name.startswith("Second")  and not item_name.startswith("SAMOSA BEEF BIG"):
                continue
            
            if is_product_bundle(item_name):
                unbundled_items = break_down_bundle(item_name)

                for item in unbundled_items:
                    

                    if item[1] in item_dict: # add qtys to already added to items list

                        print(item)

                        existing_item = item_dict[item[1]]
                        existing_item[2] += item[2] # yr_qty
                        existing_item[3] += item[3] # yr amt
                        existing_item[4] += item[4] # yr_tot_qty
                        existing_item[5] += item[5] # yr_tot_amt
                    else:
                        print(item[1] + " is not in item_dict")

                        new_data.append(item)
                        item_dict[item[1]] = item

            else: # not a bundled item
                print(item_name + " is not a bundled item") 
                # find item in unbundled_list and
                # increment it

                found = False
                for existing_item in new_data:
                    print("FOUND " + item_name) 
                    if existing_item[1] == item_name:
                        existing_item[2] += row[2]  # yr_qty
                        existing_item[3] += row[3]  # yr amt
                        existing_item[4] += row[4]  # yr_tot_qty
                        existing_item[5] += row[5]  # yr_tot_amt
                        found = True
                        break
                if not found:
                    print("APPEND " + item_name) 
                    new_data.append(row)
                    item_dict[row[1]] = row

    else: # period
        new_data = raw_data


    return new_data
