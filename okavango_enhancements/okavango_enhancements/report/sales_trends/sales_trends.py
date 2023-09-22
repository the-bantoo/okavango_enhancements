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
	# columns = get_columns(filters, "Sales Invoice")
	conditions = get_columns(filters, "Sales Invoice")
	columns = conditions['columns']
	period_list = conditions['period_list']
	
	basis = filters.get("based_on")

	"""if basis != "Item":
		data = get_sql_data(filters, basis)
	else:"""
	data = get_item_data(filters, period_list)
	
	# data = get_data(filters, conditions)

	return columns, data


def get_item_data(filters, period_list):
	query = """ select t1.item_code, SUM(IF(t1.posting_date BETWEEN '{3}' AND '{4}', (t1.actual_qty * -1), NULL)),
											SUM(IF(t1.posting_date BETWEEN '{3}' AND '{4}', ((t1.valuation_rate * t1.actual_qty) * -1), NULL)),
									SUM(IF(t1.posting_date BETWEEN '{5}' AND '{6}', (t1.actual_qty * -1), NULL)),
											SUM(IF(t1.posting_date BETWEEN '{5}' AND '{6}', ((t1.valuation_rate * t1.actual_qty) * -1), NULL)),
									SUM(IF(t1.posting_date BETWEEN '{7}' AND '{8}', (t1.actual_qty * -1), NULL)),
											SUM(IF(t1.posting_date BETWEEN '{7}' AND '{8}', ((t1.valuation_rate * t1.actual_qty) * -1), NULL)),
									SUM(IF(t1.posting_date BETWEEN '{9}' AND '{10}', (t1.actual_qty * -1), NULL)),
											SUM(IF(t1.posting_date BETWEEN '{9}' AND '{10}', ((t1.valuation_rate * t1.actual_qty) * -1), NULL)),
									SUM(IF(t1.posting_date BETWEEN '{11}' AND '{12}', (t1.actual_qty * -1), NULL)),
											SUM(IF(t1.posting_date BETWEEN '{11}' AND '{12}', ((t1.valuation_rate * t1.actual_qty) * -1), NULL)),
									SUM(IF(t1.posting_date BETWEEN '{13}' AND '{14}', (t1.actual_qty * -1), NULL)),
											SUM(IF(t1.posting_date BETWEEN '{13}' AND '{14}', ((t1.valuation_rate * t1.actual_qty) * -1), NULL)),
									SUM(IF(t1.posting_date BETWEEN '{15}' AND '{16}', (t1.actual_qty * -1), NULL)),
											SUM(IF(t1.posting_date BETWEEN '{15}' AND '{16}', ((t1.valuation_rate * t1.actual_qty) * -1), NULL)),
									SUM(IF(t1.posting_date BETWEEN '{17}' AND '{18}', (t1.actual_qty * -1), NULL)),
											SUM(IF(t1.posting_date BETWEEN '{17}' AND '{18}', ((t1.valuation_rate * t1.actual_qty) * -1), NULL)),
									SUM(IF(t1.posting_date BETWEEN '{19}' AND '{20}', (t1.actual_qty * -1), NULL)),
											SUM(IF(t1.posting_date BETWEEN '{19}' AND '{20}', ((t1.valuation_rate * t1.actual_qty) * -1), NULL)),
									SUM(IF(t1.posting_date BETWEEN '{21}' AND '{22}', (t1.actual_qty * -1), NULL)),
											SUM(IF(t1.posting_date BETWEEN '{21}' AND '{22}', ((t1.valuation_rate * t1.actual_qty) * -1), NULL)),
									SUM(IF(t1.posting_date BETWEEN '{23}' AND '{24}', (t1.actual_qty * -1), NULL)),
											SUM(IF(t1.posting_date BETWEEN '{23}' AND '{24}', ((t1.valuation_rate * t1.actual_qty) * -1), NULL)),
									SUM(IF(t1.posting_date BETWEEN '{25}' AND '{26}', (t1.actual_qty * -1), NULL)),
											SUM(IF(t1.posting_date BETWEEN '{25}' AND '{26}', ((t1.valuation_rate * t1.actual_qty) * -1), NULL)),
									SUM((t1.actual_qty * -1)), SUM(((valuation_rate * actual_qty) * -1))

				FROM `tabStock Ledger Entry` AS t1

				where (t1.company = "{0}")
					and (t1.voucher_type = "Sales Invoice")
					and (t1.is_cancelled = "0")
					and (t1.posting_date between "{1}" and "{2}")
				
				GROUP BY t1.item_code
			""".format( filters.get("company"), period_list[0][0], period_list[-1][1], 
		  				period_list[0][0], period_list[0][1], # query period dates
						period_list[1][0], period_list[1][1],
						period_list[2][0], period_list[2][1],
						period_list[3][0], period_list[3][1],
						period_list[4][0], period_list[4][1],
						period_list[5][0], period_list[5][1],
						period_list[6][0], period_list[6][1],
						period_list[7][0], period_list[7][1],
						period_list[8][0], period_list[8][1],
						period_list[9][0], period_list[9][1],
						period_list[10][0], period_list[10][1],
						period_list[11][0], period_list[11][1]
					)
	

	query = """ select t1.item_code, SUM(IF(t1.posting_date BETWEEN '{3}' AND '{4}', (t1.actual_qty * -1), NULL)),											
									SUM(IF(t1.posting_date BETWEEN '{5}' AND '{6}', (t1.actual_qty * -1), NULL)),
									SUM(IF(t1.posting_date BETWEEN '{7}' AND '{8}', (t1.actual_qty * -1), NULL)),
									SUM(IF(t1.posting_date BETWEEN '{9}' AND '{10}', (t1.actual_qty * -1), NULL)),
									SUM(IF(t1.posting_date BETWEEN '{11}' AND '{12}', (t1.actual_qty * -1), NULL)),
									SUM(IF(t1.posting_date BETWEEN '{13}' AND '{14}', (t1.actual_qty * -1), NULL)),
									SUM(IF(t1.posting_date BETWEEN '{15}' AND '{16}', (t1.actual_qty * -1), NULL)),
									SUM(IF(t1.posting_date BETWEEN '{17}' AND '{18}', (t1.actual_qty * -1), NULL)),
									SUM(IF(t1.posting_date BETWEEN '{19}' AND '{20}', (t1.actual_qty * -1), NULL)),
									SUM(IF(t1.posting_date BETWEEN '{21}' AND '{22}', (t1.actual_qty * -1), NULL)),
									SUM(IF(t1.posting_date BETWEEN '{23}' AND '{24}', (t1.actual_qty * -1), NULL)),
									SUM(IF(t1.posting_date BETWEEN '{25}' AND '{26}', (t1.actual_qty * -1), NULL)),
									SUM((t1.actual_qty * -1))

				FROM `tabStock Ledger Entry` AS t1

				where (t1.company = "{0}")
					and (t1.voucher_type = "Sales Invoice")
					and (t1.is_cancelled = "0")
					and (t1.posting_date between "{1}" and "{2}")
				
				GROUP BY t1.item_code
			""".format( filters.get("company"), period_list[0][0], period_list[-1][1], 
		  				period_list[0][0], period_list[0][1], # query period dates
						period_list[1][0], period_list[1][1],
						period_list[2][0], period_list[2][1],
						period_list[3][0], period_list[3][1],
						period_list[4][0], period_list[4][1],
						period_list[5][0], period_list[5][1],
						period_list[6][0], period_list[6][1],
						period_list[7][0], period_list[7][1],
						period_list[8][0], period_list[8][1],
						period_list[9][0], period_list[9][1],
						period_list[10][0], period_list[10][1],
						period_list[11][0], period_list[11][1]
					)
	
	data = frappe.db.sql(
			query,
			as_list=1,
		)
	
	return data


def get_columns(filters, trans):
	validate_filters(filters)

	# get conditions for based_on filter cond
	based_on_details = based_wise_columns_query(filters.get("based_on"), trans)
	# get conditions for periodic filter cond
	period_cols, period_select, period_list = period_wise_columns_query(filters, trans)
	# get conditions for grouping filter cond
	group_by_cols = group_wise_column(filters.get("group_by"))

	columns = (
		based_on_details["based_on_cols"]
		+ period_cols
		+ [_("Total(Qty)") + ":Float:120"]
	)
	if group_by_cols:
		columns = (
			based_on_details["based_on_cols"]
			+ group_by_cols
			+ period_cols
			+ [_("Total(Qty)") + ":Float:120"]
		)

	conditions = {
		"based_on_select": based_on_details["based_on_select"],
		"period_wise_select": period_select,
		"columns": columns,
		"group_by": based_on_details["based_on_group_by"],
		"grbc": group_by_cols,
		"trans": trans,
		"addl_tables": based_on_details["addl_tables"],
		"addl_tables_relational_cond": based_on_details.get("addl_tables_relational_cond", ""),
		"period_list": period_list or [],
	}

	return conditions

def get_list_dict_by_key(data_list, key, value):
	for row in data_list:
		if row.get(key) == value:
			return row
	return False

def pprint(args):
	return
	pp.pprint(args)


def period_wise_columns_query(filters, trans):
	query_details = ""
	pwc = []
	bet_dates = get_period_date_ranges(filters.get("period"), filters.get("fiscal_year"))

	if trans in ["Purchase Receipt", "Delivery Note", "Purchase Invoice", "Sales Invoice"]:
		trans_date = "posting_date"
		if filters.period_based_on:
			trans_date = filters.period_based_on
	else:
		trans_date = "transaction_date"

	if filters.get("period") != "Yearly":
		for dt in bet_dates:
			get_period_wise_columns(dt, filters.get("period"), pwc)
			query_details = get_period_wise_query(dt, trans_date, query_details)
	else:
		pwc = [
			_(filters.get("fiscal_year")) + " (" + _("Qty") + "):Float:120",
		]
		query_details = " SUM(t2.stock_qty), SUM(t2.base_net_amount),"

	query_details += "SUM(t2.stock_qty), SUM(t2.base_net_amount)"
	return pwc, query_details, bet_dates


def based_wise_columns_query(based_on, trans):
	based_on_details = {}

	# based_on_cols, based_on_select, based_on_group_by, addl_tables
	if based_on == "Item":
		based_on_details["based_on_cols"] = ["Item Name:Data:120"]
		based_on_details["based_on_select"] = "t2.item_code, t2.item_name,"
		based_on_details["based_on_group_by"] = "t2.item_code"
		based_on_details["addl_tables"] = ""

	elif based_on == "Item Group":
		based_on_details["based_on_cols"] = ["Item Group:Link/Item Group:120"]
		based_on_details["based_on_select"] = "t2.item_group,"
		based_on_details["based_on_group_by"] = "t2.item_group"
		based_on_details["addl_tables"] = ""

	elif based_on == "Customer":
		based_on_details["based_on_cols"] = [
			"Customer:Link/Customer:120",
			"Territory:Link/Territory:120",
		]
		based_on_details["based_on_select"] = "t1.customer_name, t1.territory, "
		based_on_details["based_on_group_by"] = (
			"t1.party_name" if trans == "Quotation" else "t1.customer"
		)
		based_on_details["addl_tables"] = ""

	elif based_on == "Customer Group":
		based_on_details["based_on_cols"] = ["Customer Group:Link/Customer Group"]
		based_on_details["based_on_select"] = "t1.customer_group,"
		based_on_details["based_on_group_by"] = "t1.customer_group"
		based_on_details["addl_tables"] = ""

	elif based_on == "Supplier":
		based_on_details["based_on_cols"] = [
			"Supplier:Link/Supplier:120",
			"Supplier Group:Link/Supplier Group:140",
		]
		based_on_details["based_on_select"] = "t1.supplier, t3.supplier_group,"
		based_on_details["based_on_group_by"] = "t1.supplier"
		based_on_details["addl_tables"] = ",`tabSupplier` t3"
		based_on_details["addl_tables_relational_cond"] = " and t1.supplier = t3.name"

	elif based_on == "Supplier Group":
		based_on_details["based_on_cols"] = ["Supplier Group:Link/Supplier Group:140"]
		based_on_details["based_on_select"] = "t3.supplier_group,"
		based_on_details["based_on_group_by"] = "t3.supplier_group"
		based_on_details["addl_tables"] = ",`tabSupplier` t3"
		based_on_details["addl_tables_relational_cond"] = " and t1.supplier = t3.name"

	elif based_on == "Territory":
		based_on_details["based_on_cols"] = ["Territory:Link/Territory:120"]
		based_on_details["based_on_select"] = "t1.territory,"
		based_on_details["based_on_group_by"] = "t1.territory"
		based_on_details["addl_tables"] = ""

	elif based_on == "Project":
		if trans in ["Sales Invoice", "Delivery Note", "Sales Order"]:
			based_on_details["based_on_cols"] = ["Project:Link/Project:120"]
			based_on_details["based_on_select"] = "t1.project,"
			based_on_details["based_on_group_by"] = "t1.project"
			based_on_details["addl_tables"] = ""
		elif trans in ["Purchase Order", "Purchase Invoice", "Purchase Receipt"]:
			based_on_details["based_on_cols"] = ["Project:Link/Project:120"]
			based_on_details["based_on_select"] = "t2.project,"
			based_on_details["based_on_group_by"] = "t2.project"
			based_on_details["addl_tables"] = ""
		else:
			frappe.throw(_("Project-wise data is not available for Quotation"))

	return based_on_details


def get_period_wise_columns(bet_dates, period, pwc):
	if period == "Monthly":
		pwc += [
			_(get_mon(bet_dates[0])) + " (" + _("Qty") + "):Float:120",
		]
	else:
		pwc += [
			_(get_mon(bet_dates[0])) + "-" + _(get_mon(bet_dates[1])) + " (" + _("Qty") + "):Float:120",
		]

"""
add delivery_note check
add force bundle breakdown

"""



def get_item_data_freeze(filters, period_list):
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
				'posting_date', 'between', [ filters.get('period_start'), filters.get('period_end') ]
			]
		]
	)
	for invoice in invoices:
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

def get_columns_freeze(filters, inv):
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

