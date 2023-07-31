# Copyright (c) 2023, Bantoo and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from erpnext.controllers.trends import *
import pprint
pp = pprint.PrettyPrinter(indent=4)


def execute(filters=None):
    if not filters:
        filters = {}
    data = []
    columns = get_columns(filters, "Sales Invoice")
    
    basis = filters.get("based_on")

    if basis != "Item":
        data = get_sql_data(filters, basis)
    else:
        data = get_item_data(filters)

    return columns, data

def get_list_dict_by_key(data_list, key, value):
    for row in data_list:
        if row.get(key) == value:
            return row
    return False

def pprint(args):
    return
    pp.pprint(args)

"""
add delivery_note check
add force bundle breakdown

"""
def get_item_data(filters):
    data = []
    
    invoices = frappe.get_all("Sales Invoice", 
		fields = [ 'posting_date', 'name', 'grand_total'],
    	order_by='posting_date asc',
        limit=0,
		filters = [
			[	
				'docstatus', '=', 1
			],
			[
				'posting_date', 'between', [ filters.get("from_date"), filters.get("to_date")]
			]
		]
	)
    
    for invoice in invoices:
        """
        print("")
        print("INVOICE")
        print("")

        print(invoice)
        
        print("")
        print(items)
        print("")
        print(p_items)
        print("")"""
        
        items = []
        p_items = []

        items = frappe.get_all("Sales Invoice Item", 
            fields = [ 'qty', 'amount', 'item_code'],
            order_by='item_code asc',
            filters = [
                [	
                    'parent', '=', invoice.name
                ]
            ]
        )

        p_items = frappe.get_all("Packed Item", 
            fields = [ 'parent_item', 'item_code', 'qty' ],
            order_by='item_code asc',
            filters = [
                [	
                    'parent', '=', invoice.name
                ]
            ]
        )

        for item in items:
            packed_item = get_list_dict_by_key(p_items, 'parent_item', item.item_code)
            
            if packed_item:
                
                # check if item exists in data and add item to data 
                # or append a new item to data
                existing_item = get_list_dict_by_key(data, 'item_code', packed_item['item_code'])
                
                if existing_item:
                    # Update existing item in data
                    existing_item['qty'] += packed_item['qty']
                    existing_item['amount'] += item.amount
                    print("incremented 1")
                else:
                    # Append a new item to data

                    data.append({
                        "item_code": packed_item.item_code,
                        "qty": packed_item.qty,
                        "amount": item.amount
                    })
                    print("append 1: " + packed_item.item_code)
            else:           
                pprint(item.item_code)     
                # check if item exists in data and add item to data 
                # or append a new item to data
                existing_item = get_list_dict_by_key(data, 'item_code', item['item_code'])
                
                if existing_item:
                    # Update existing item in data
                    existing_item['qty'] += item['qty']
                    existing_item['amount'] += item.amount
                    print("incremented 2")
                else:
                    data.append({
                        "item_code": item.item_code,
                        "qty": item.qty,
                        "amount": item.amount
                    })
                    print("append 2: " + str(item.item_code))

    """
    print("")
    pprint("data")
    print("")
    pp.pprint(data)
    """

    return data

def get_sql_data(filters, basis):
    # t2.item_code AS item_code,
    # and t3.item_code = "Second Nicest Strips" or t2.item_code = "Second Nicest Strips"
    # COALESCE(t3.qty, t2.qty) AS qty
    
    query = ""
        
    if basis == "Item Group":
        
        query = """ select t2.item_group AS item_group, SUM(t2.qty) AS qty, SUM(t2.amount) as amount

                FROM `tabSales Invoice` AS t1
                JOIN `tabSales Invoice Item` AS t2 ON t1.name = t2.parent

                where t1.company = "{0}" 
                    and t1.docstatus = 1
                    and t1.posting_date between "{1}" and "{2}"
                
                GROUP BY t2.item_group
                ORDER BY t2.item_group asc
                """.format( filters.get("company"), filters.get("from_date"), filters.get("to_date") )

        

    elif basis == "Territory":
        """query = "" select customer.territory AS territory, COALESCE(t3.item_code, t2.item_code) AS item, SUM(COALESCE(t3.qty, t2.qty)) AS qty, SUM(t2.amount) as amount

                FROM `tabSales Invoice` AS t1
                LEFT JOIN `tabSales Invoice Item` AS t2 ON t1.name = t2.parent
                LEFT JOIN `tabPacked Item` AS t3 ON t2.item_code = t3.parent_item
                LEFT JOIN `tabCustomer` AS customer ON t1.customer = customer.name

                where t1.company = "{0}" 
                    and t1.docstatus = 1
                    and t1.posting_date between "{1}" and "{2}"
                
                
                GROUP BY t2.item_code, customer.territory
                ORDER BY customer.territory asc, t2.item_code asc
                "".format( filters.get("company"), filters.get("from_date"), filters.get("to_date") )"""
        
        query = """ select customer.territory AS territory, t2.item_code AS item, SUM(t2.qty) AS qty, SUM(t2.amount) as amount

                FROM `tabSales Invoice` AS t1
                JOIN `tabSales Invoice Item` AS t2 ON t1.name = t2.parent
                JOIN `tabCustomer` AS customer ON t1.customer = customer.name

                where t1.company = "{0}" 
                    and t1.docstatus = 1
                    and t1.posting_date between "{1}" and "{2}"
                
                GROUP BY t2.item_code, customer.territory
                ORDER BY customer.territory asc, t2.item_code asc
                """.format( filters.get("company"), filters.get("from_date"), filters.get("to_date") )


    elif basis == "Customer Group":
        query = """ select customer.customer_group AS customer_group, SUM(t2.amount) as amount

                FROM `tabSales Invoice` AS t1
                LEFT JOIN `tabSales Invoice Item` AS t2 ON t1.name = t2.parent
                LEFT JOIN `tabCustomer` AS customer ON t1.customer = customer.name

                where t1.company = "{0}" 
                    and t1.docstatus = 1
                    and t1.posting_date between "{1}" and "{2}"
                
                GROUP BY customer.customer_group
                ORDER BY customer.customer_group asc
                """.format( filters.get("company"), filters.get("from_date"), filters.get("to_date") )
        
    elif basis == "Customer":
        query = """ select customer.name AS customer, SUM(t2.amount) as amount

                FROM `tabSales Invoice` AS t1
                LEFT JOIN `tabSales Invoice Item` AS t2 ON t1.name = t2.parent
                LEFT JOIN `tabCustomer` AS customer ON t1.customer = customer.name

                where t1.company = "{0}" 
                    and t1.docstatus = 1
                    and t1.posting_date between "{1}" and "{2}"
                
                
                GROUP BY customer.name
                ORDER BY customer.name asc
                """.format( filters.get("company"), filters.get("from_date"), filters.get("to_date") )

    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    print(query)
    
    data = frappe.db.sql(
            query,
            as_list=1,
    )
    pp.pprint(data)

    #print(data)

    return data

def nope(s):
    pass

def get_columns(filters, inv):
    """return columns"""
    basis = filters.get("based_on")
    main_column = {}
    if basis == "Item Group":
        main_column = [
            {
                "label": _("Item Group"),
                "fieldname": "item_group",
                "fieldtype": "Link",
                "options": "Item Group",
                'align': 'left',
                "width": 500,
            }
        ]
        
    elif basis == "Item":
        main_column = [
            {
                "label": _("Item"),
                "fieldname": "item_code",
                "fieldtype": "Link",
                "options": "Item",
                'align': 'left',
                "width": 500,
            }
        ]
    elif basis == "Territory":
        main_column = [
            {
                "label": _("Territory"),
                "fieldname": "territory",
                "fieldtype": "Link",
                "options": "Territory",
                'align': 'left',
                "width": 200,
            },
            {
                "label": _("Item"),
                "fieldname": "item_code",
                "fieldtype": "Link",
                "options": "Item",
                'align': 'left',
                "width": 400,
            }
        ]
    elif basis == "Customer Group":
        main_column = [
            {
                "label": _("Customer Group"),
                "fieldname": "customer_group",
                "fieldtype": "Link",
                "options": "Customer Group",
                'align': 'left',
                "width": 200,
            }
        ]
    elif basis == "Customer":
        main_column = [
            {
                "label": _("Customer"),
                "fieldname": "customer",
                "fieldtype": "Link",
                "options": "Customer",
                'align': 'left',
                "width": 200,
            }
        ]
        

    columns = [
        {
            "label": _("Qty"),
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 150,
            "precision": 2
        },
        {
            "label": _("Amount"),
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 200,
            "options": "currency",
        }
    ]
    if basis == "Customer Group" or basis == "Customer":
        columns.pop(-2)

    return main_column + columns

"""
    select t2.item_code, t2.item_name, SUM(t2.stock_qty), SUM(t2.base_net_amount),SUM(t2.stock_qty), SUM(t2.base_net_amount), t1.name from `tabSales Invoice` t1, `tabSales Invoice Item` t2 
    where t2.parent = t1.name and t1.company = %s and t1.posting_date between %s and %s and
    t1.docstatus = 1  
    group by t2.item_code
                    """


def is_product_bundle(item_name):

    # Check if there are any Product Bundle records where parent_item matches item_name
    # The "Product Bundle" string may need to be replaced based on your specific setup
    return frappe.db.exists("Product Bundle", {"new_item_code": item_name})

"""def break_down_bundle(item_name):
    bundle_doc = frappe.get_doc("Product Bundle", item_name)
    items = []


    for bundle_item in bundle_doc.items:
        rate = frappe.db.get_value('Item', bundle_item.item_code, 'standard_rate')
        amount = bundle_item.qty * rate
        items.append([bundle_item.item_code, bundle_item.item_code, bundle_item.qty, amount, bundle_item.qty, amount])
        
    return items"""

def print2(text):
    return
    frappe.errprint(text)

def print(text):
    return
    frappe.errprint(text)

def get_data_with_bundle_breakdown(filters, conditions):
    raw_data = []
    new_data = []
    item_dict = {}

    period = filters.get("period")
    unbundle_items = filters.get("unbundle_items")
    based_on = filters.get("based_on")

    if unbundle_items != 1 or based_on != "Item":
        return get_data(filters, conditions)

    if period == "Yearly":
        raw_data = get_data_local(filters, conditions)

        for row in raw_data:
            item_name = row[1] # select the item_name from the row

            # only debug items
            #if not item_name.startswith("Chicken Samosa Wholesale(Pack100)") and not item_name.startswith("Nice") and not item_name.startswith("Second")  and not item_name.startswith("SAMOSA BEEF BIG"):
            #    continue
            
            if is_product_bundle(item_name):
                unbundled_items = break_down_bundle(item_name, row[-1])

                for item in unbundled_items:
                    print("item " + " " + str(item[1]) + " from " + row[-1])
                    item[0] = item_name
                    if item[1] in item_dict: 
                        # add qtys to an item already in items list
                        print("added " + str(item_dict[item[1]][1]))
                        existing_item = item_dict[item[1]]
                        existing_item[2] += item[2] # yr_qty
                        existing_item[3] += item[3] # yr amt
                        existing_item[4] += item[4] # yr_tot_qty
                        existing_item[5] += item[5] # yr_tot_amt
                    else:
                        print(item[1] + " is not in item_dict")

                        new_data.append(item)
                        item_dict[item[1]] = item # array with idx whose id is the item_name

            else: # not a bundled item
                print(item_name + " is not a bundled item") 
                # find item in unbundled_list and
                # increment it
                print("row: " + str(row[1]) + " ")

                found = False
                for existing_item in new_data:
                    
                    if existing_item[1] == item_name:
                        print("FOUND " + item_name) 
                        
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


        print("END OF ROW")

    else: # period
        new_data = get_data(filters, conditions)


    return new_data




def break_down_bundle(item_name, invoice_no):
    items = []

    # Get the stock ledger entries that are linked to the specified invoice
    stock_ledger_entries = frappe.get_all(
        "Stock Ledger Entry",
        filters={
            "voucher_type": "Sales Invoice",
            "voucher_no": invoice_no
        },
        fields=["item_code", "actual_qty", "valuation_rate"]
    )
    # frappe.get_cached_value(taxes_and_charges_doctype, self.taxes_and_charges, "disabled")
    

    for entry in stock_ledger_entries:
        item_name = frappe.get_cached_value("Item", "item_name", entry.item_code)
        item_code = entry.item_code
        qty = entry.actual_qty * -1
        rate = entry.valuation_rate
        amount = qty * rate

        items.append([item_name, item_code, qty, amount, qty, amount])

    return items

def get_data_local(filters, conditions):
    data = []
    inc, cond = "", ""
    query_details = conditions["based_on_select"] + conditions["period_wise_select"] + ", t1.name"

    #print(query_details)

    posting_date = "t1.transaction_date"
    if conditions.get("trans") in [
        "Sales Invoice",
        "Purchase Invoice",
        "Purchase Receipt",
        "Delivery Note",
    ]:
        posting_date = "t1.posting_date"
        if filters.period_based_on:
            posting_date = "t1." + filters.period_based_on

    if conditions["based_on_select"] in ["t1.project,", "t2.project,"]:
        cond = " and " + conditions["based_on_select"][:-1] + " IS Not NULL"
    if conditions.get("trans") in ["Sales Order", "Purchase Order"]:
        cond += " and t1.status != 'Closed'"

    if conditions.get("trans") == "Quotation" and filters.get("group_by") == "Customer":
        cond += " and t1.quotation_to = 'Customer'"

    year_start_date, year_end_date = frappe.db.get_value(
        "Fiscal Year", filters.get("fiscal_year"), ["year_start_date", "year_end_date"]
    )

    if filters.get("group_by"):
        sel_col = ""
        ind = conditions["columns"].index(conditions["grbc"][0])

        if filters.get("group_by") == "Item":
            sel_col = "t2.item_code"
        elif filters.get("group_by") == "Customer":
            sel_col = "t1.party_name" if conditions.get("trans") == "Quotation" else "t1.customer"
        elif filters.get("group_by") == "Supplier":
            sel_col = "t1.supplier"

        if filters.get("based_on") in ["Item", "Customer", "Supplier"]:
            inc = 2
        else:
            inc = 1
        data1 = frappe.db.sql(
            """ select %s from `tab%s` t1, `tab%s Item` t2 %s
                    where t2.parent = t1.name and t1.company = %s and %s between %s and %s and
                    t1.docstatus = 1 %s %s
                    group by %s
                """
            % (
                query_details,
                conditions["trans"],
                conditions["trans"],
                conditions["addl_tables"],
                "%s",
                posting_date,
                "%s",
                "%s",
                conditions.get("addl_tables_relational_cond"),
                cond,
                conditions["group_by"],
            ),
            (filters.get("company"), year_start_date, year_end_date),
            as_list=1,
        )

        for d in range(len(data1)):
            # to add blanck column
            dt = data1[d]
            dt.insert(ind, "")
            data.append(dt)

            # to get distinct value of col specified by group_by in filter
            row = frappe.db.sql(
                """select DISTINCT(%s) from `tab%s` t1, `tab%s Item` t2 %s
                        where t2.parent = t1.name and t1.company = %s and %s between %s and %s
                        and t1.docstatus = 1 and %s = %s %s %s
                    """
                % (
                    sel_col,
                    conditions["trans"],
                    conditions["trans"],
                    conditions["addl_tables"],
                    "%s",
                    posting_date,
                    "%s",
                    "%s",
                    conditions["group_by"],
                    "%s",
                    conditions.get("addl_tables_relational_cond"),
                    cond,
                ),
                (filters.get("company"), year_start_date, year_end_date, data1[d][0]),
                as_list=1,
            )

            for i in range(len(row)):
                des = ["" for q in range(len(conditions["columns"]))]

                # get data for group_by filter
                row1 = frappe.db.sql(
                    """ select %s , %s from `tab%s` t1, `tab%s Item` t2 %s
                            where t2.parent = t1.name and t1.company = %s and %s between %s and %s
                            and t1.docstatus = 1 and %s = %s and %s = %s %s %s
                        """
                    % (
                        sel_col,
                        conditions["period_wise_select"],
                        conditions["trans"],
                        conditions["trans"],
                        conditions["addl_tables"],
                        "%s",
                        posting_date,
                        "%s",
                        "%s",
                        sel_col,
                        "%s",
                        conditions["group_by"],
                        "%s",
                        conditions.get("addl_tables_relational_cond"),
                        cond,
                    ),
                    (filters.get("company"), year_start_date, year_end_date, row[i][0], data1[d][0]),
                    as_list=1,
                )

                des[ind] = row[i][0]

                for j in range(1, len(conditions["columns"]) - inc):
                    des[j + inc] = row1[0][j]

                data.append(des)
    else:
        data = frappe.db.sql(
            """ select %s from `tab%s` t1, `tab%s Item` t2 %s
                    where t2.parent = t1.name and t1.company = %s and %s between %s and %s and
                    t1.docstatus = 1 %s %s
                    group by %s
                """
            % (
                query_details,
                conditions["trans"],
                conditions["trans"],
                conditions["addl_tables"],
                "%s",
                posting_date,
                "%s",
                "%s",
                cond,
                conditions.get("addl_tables_relational_cond", ""),
                conditions["group_by"],
            ),
            (filters.get("company"), year_start_date, year_end_date),
            as_list=1,
        )

        print(
            """ select %s from `tab%s` t1, `tab%s Item` t2 %s
                    where t2.parent = t1.name and t1.company = %s and %s between %s and %s and
                    t1.docstatus = 1 %s %s
                    group by %s
                """
            % (
                query_details,
                conditions["trans"],
                conditions["trans"],
                conditions["addl_tables"],
                "%s",
                posting_date,
                "%s",
                "%s",
                cond,
                conditions.get("addl_tables_relational_cond", ""),
                conditions["group_by"],
            )
        )

    #print(data)

    return data

