# Copyright (c) 2023, Bantoo and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import pprint


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data



def get_data(filters):
    
    customer = filters.get("customer")
    query = ""
    customer_selection = ""

    if customer != None:
        customer_selection = 'and customer.name = "{}"'.format(customer)

    query = """ select COALESCE(t3.item_code, t2.item_code) as item, SUM(COALESCE(t3.qty, t2.qty)) AS qty, SUM(t2.amount) as amount, t1.name, t1.grand_total

                FROM `tabSales Invoice` AS t1
                LEFT JOIN `tabSales Invoice Item` AS t2 ON t1.name = t2.parent
                LEFT JOIN `tabPacked Item` AS t3 ON t1.name = t3.parent and t3.parent_item = t2.item_code

                where t1.company = "{0}" 
                    and t1.docstatus = 1
                    and t1.posting_date between "{1}" and "{2}"
                    /* and t2.item_code LIKE "%Nice%" or t3.item_code LIKE "%Nice%" */
                
                
                GROUP BY COALESCE(t3.item_code, t2.item_code)
                ORDER BY COALESCE(t3.item_code, t2.item_code) asc
                """.format( filters.get("company"), filters.get("from_date"), filters.get("to_date") )
    
    query = """ select t3.item_code, t2.item_code as item, COALESCE(t3.qty, t2.qty) AS qty, ( t2.amount) as amount, t1.name, t1.grand_total

                FROM `tabSales Invoice` AS t1
                LEFT JOIN `tabSales Invoice Item` AS t2 ON t1.name = t2.parent
                LEFT JOIN `tabPacked Item` AS t3 ON t1.name = t3.parent and t3.parent_item = t2.item_code

                where t1.company = "{0}" 
                    and t1.docstatus = 1
                    and t1.posting_date between "{1}" and "{2}"
                    /* and t2.item_code LIKE "%Nice%" or t3.item_code LIKE "%Nice%" */
                
                
                /*GROUP BY COALESCE(t3.item_code, t2.item_code)
                ORDER BY COALESCE(t3.item_code, t2.item_code) asc*/
                
                order by t1.name
                """.format( filters.get("company"), filters.get("from_date"), filters.get("to_date") )
    
    query = """ select t1.posting_date, t1.name as invoice, customer.name AS customer, COALESCE(t3.item_code, t2.item_code) as item, COALESCE(t3.batch_no, t2.batch_no) as batch_no, t4.manufacturing_date as manufacturing_date, t4.expiry_date as expiry_date, COALESCE(t3.qty, t2.qty) as qty, SUM(t2.amount) as amount

                FROM `tabSales Invoice` AS t1
                LEFT JOIN `tabSales Invoice Item` AS t2 ON t1.name = t2.parent
                LEFT JOIN `tabCustomer` AS customer ON t1.customer = customer.name
                LEFT JOIN `tabPacked Item` AS t3 ON t1.name = t3.parent and t3.parent_item = t2.item_code
                LEFT JOIN `tabBatch` AS t4 ON t3.batch_no = t4.name or t2.batch_no = t4.name

                where (t1.company = "{0}" )
                    and (t1.docstatus = 1)
                    and (t1.posting_date between "{1}" and "{2}")
                    and (t2.batch_no IS NOT NULL or t3.batch_no IS NOT NULL)
                    {3}
                
                GROUP BY customer.name, COALESCE(t3.item_code, t2.item_code)
                ORDER BY t1.posting_date asc, customer.name, COALESCE(t3.item_code, t2.item_code) 
            """.format( filters.get("company"), filters.get("from_date"), filters.get("to_date"), customer_selection )
    
    pp = pprint.PrettyPrinter(indent=4)
    print(query)
    
    data = frappe.db.sql(
            query,
            as_dict=1,
    )
    # pp.pprint(data)

    #print(data)

    return data

def nope(s):
    pass

def get_columns(filters):
    """return columns"""

    columns = [

        {
            "label": _("Posting Date"),
            "fieldname": "posting_date",
            "fieldtype": "Data",
            'align': 'left',
            "width": 100,
        },
        {
            "label": _("Customer"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            'align': 'left',
            "width": 220,
        },
        {
            "label": _("Invoice"),
            "fieldname": "invoice",
            "fieldtype": "Link",
            "options": "Sales Invoice",
            'align': 'left',
            "width": 80,
        },
        {
            "label": _("Item"),
            "fieldname": "item",
            "fieldtype": "Link",
            "options": "Item",
            'align': 'left',
            "width": 300,
        },
        {
            "label": _("Batch"),
            "fieldname": "batch_no",
            "fieldtype": "Link",
            "options": "Batch",
            'align': 'right',
            "width": 120,
        },
        {
            "label": _("Manufacture"),
            "fieldname": "manufacturing_date",
            "fieldtype": "date",
            'align': 'right',
            "width": 120,
        },
        {
            "label": _("Expiry"),
            "fieldname": "expiry_date",
            "fieldtype": "date",
            'align': 'right',
            "width": 100,
        },
        {
            "label": _("Qty"),
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 100,
            "precision": 2
        }
    ]

    return columns
