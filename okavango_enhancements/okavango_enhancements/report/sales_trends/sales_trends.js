// Copyright (c) 2023, Bantoo and contributors
// For license information, please see license.txt
/* eslint-disable */

// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Sales Trends"] = {
	"filters": [
		{
			"fieldname":"period",
			"label": __("Period"),
			"fieldtype": "Select",
			"hidden": 1,
			"options": [
				{ "value": "Monthly", "label": __("Monthly") },
				{ "value": "Quarterly", "label": __("Quarterly") },
				{ "value": "Half-Yearly", "label": __("Half-Yearly") },
				{ "value": "Yearly", "label": __("Yearly") }
			],
			"default": "Monthly"
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.get_today(),
		},
		{
			"fieldname":"based_on",
			"label": __("Based On"),
			"fieldtype": "Select",
			"hidden": 1,
			"options": [
				{ "value": "Item", "label": __("Item") },
				{ "value": "Item Group", "label": __("Item Group") },
				{ "value": "Customer", "label": __("Customer") },
				{ "value": "Customer Group", "label": __("Customer Group") },
				{ "value": "Territory", "label": __("Territory") }
			],
			"default": "Item",
			"hidden": 0,
			"dashboard_config": {
				"read_only": 1,
			}
		},
		{
			"fieldname":"fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"hidden": 1,
			"options":'Fiscal Year',
			"default": frappe.sys_defaults.fiscal_year
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname":"unbundle_items",
			"label": __("Unbundle Items"),
			"hidden": 1,
			"fieldtype": "Check"
		}
	]
}

