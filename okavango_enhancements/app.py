
import frappe
from frappe import _
from frappe.utils import today
from frappe.query_builder.functions import CombineDatetime, CurDate, Sum

@frappe.whitelist()
def get_batches():
    batch = frappe.qb.DocType("Batch")
    bin = frappe.qb.DocType("Bin")

    query = (
        frappe.qb.from_(batch)
        .join(bin)
        .on(batch.item == bin.item_code)
        .select(
            batch.batch_id.as_("name"),
            batch.item,
            batch.item_name,
            batch.manufacturing_date,
            batch.expiry_date,
            batch.batch_qty,
            bin.warehouse.as_("warehouse"),
            Sum(bin.actual_qty).as_("qty")
        )
        .where(
            (bin.actual_qty > 0)
            & (batch.batch_qty > 0)
            & (batch.disabled == 0)
            & ((batch.expiry_date >= CurDate()) | (batch.expiry_date.isnull()))
        )
        .groupby(bin.warehouse, batch.batch_id)
        .orderby(batch.manufacturing_date, bin.actual_qty)
    )
    
    items = get_items()
    
    return {
        'batches': query.run(as_dict=True), 
        'items': items
    }

def get_items():
    return frappe.get_list('Item', fields={'item_code', 'has_batch_no'}, limit=0)