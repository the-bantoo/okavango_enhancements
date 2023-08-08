
import frappe
from frappe import _
from frappe.utils import today, cint, flt, get_link_to_form, nowtime
from frappe.query_builder.functions import CombineDatetime, CurDate, Sum
import json


frappe.flags.hide_serial_batch_dialog = True;


"""def get_batches(throw=False, serial_no=None, with_items=True):
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
            (batch.item == 'Samosa Chicken')
            &(bin.actual_qty > 0)
            & (batch.batch_qty > 0)
            & (batch.disabled == 0)
            & ((batch.expiry_date >= CurDate()) | (batch.expiry_date.isnull()))
        )
        .groupby(bin.warehouse, batch.batch_id)
        .orderby(batch.manufacturing_date, batch.batch_qty)
    )
    if with_items:         
        items = get_items()
        
        return {
            'batches': query.run(as_dict=True), 
            'items': items
        }
    else:
        return query.run(as_dict=True)
"""

def get_items():
    return frappe.get_list('Item', fields={'item_code', 'has_batch_no'}, limit=0)

@frappe.whitelist()
def get_batches(item_code=None, warehouse=None, qty=1, throw=False, serial_no=None, with_items=True):
    from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos

    batch = frappe.qb.DocType("Batch")
    sle = frappe.qb.DocType("Stock Ledger Entry")

    query = (
        frappe.qb.from_(batch)
        .join(sle)
        .on(batch.batch_id == sle.batch_no)
        .select(
            batch.batch_id.as_("name"),
            Sum(sle.actual_qty).as_("batch_qty"),
            batch.batch_qty.as_("old_batch_qty"),
            batch.item,
            batch.item_name,
            batch.manufacturing_date,
            batch.expiry_date,
            sle.warehouse,
            Sum(sle.actual_qty).as_("qty"),
        )
        .where(
            (sle.is_cancelled == 0)
            & (batch.batch_qty > 0)
            & (batch.disabled == 0)
            & ((batch.expiry_date >= CurDate()) | (batch.expiry_date.isnull()))
        )
        .groupby(sle.warehouse, batch.batch_id)
        .orderby(batch.expiry_date, batch.creation)
    )

    if serial_no and frappe.get_cached_value("Item", item_code, "has_batch_no"):
        serial_nos = get_serial_nos(serial_no)
        batches = frappe.get_all(
            "Serial No",
            fields=["distinct batch_no"],
            filters={"item_code": item_code, "warehouse": warehouse, "name": ("in", serial_nos)},
        )
        
        if not batches:
            from erpnext.stock.doctype.batch.batch import validate_serial_no_with_batch
            validate_serial_no_with_batch(serial_nos, item_code)

        if batches and len(batches) > 1:
            return []

        query = query.where(batch.name == batches[0].batch_no)

    if with_items:         
        items = get_items()
        
        return {
            'batches': query.run(as_dict=True), 
            'items': items
        }
    else:
        return query.run(as_dict=True)

def get_item_batches(item_code, warehouse, qty=1, throw=False, serial_no=None):
    from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos

    batch = frappe.qb.DocType("Batch")
    sle = frappe.qb.DocType("Stock Ledger Entry")

    query = (
        frappe.qb.from_(batch)
        .join(sle)
        .on(batch.batch_id == sle.batch_no)
        .select(
            batch.batch_id,
            Sum(sle.actual_qty).as_("qty"),
        )
        .where(
            (sle.item_code == item_code)
            & (sle.warehouse == warehouse)
            & (sle.is_cancelled == 0)
            & ((batch.expiry_date >= CurDate()) | (batch.expiry_date.isnull()))
        )
        .groupby(batch.batch_id)
        .orderby(batch.expiry_date, batch.creation)
    )

    if serial_no and frappe.get_cached_value("Item", item_code, "has_batch_no"):
        serial_nos = get_serial_nos(serial_no)
        batches = frappe.get_all(
            "Serial No",
            fields=["distinct batch_no"],
            filters={"item_code": item_code, "warehouse": warehouse, "name": ("in", serial_nos)},
        )

        if not batches:
            from erpnext.stock.doctype.batch.batch import validate_serial_no_with_batch
            validate_serial_no_with_batch(serial_nos, item_code)

        if batches and len(batches) > 1:
            return []

        query = query.where(batch.name == batches[0].batch_no)

    return query.run(as_dict=True)       



def _print(*args):
    #return
    def stringify(arg):
        if isinstance(arg, (dict, list)):
            return json.dumps(arg)
        return str(arg)

    formatted_args = [stringify(arg) for arg in args]
    print(*formatted_args)

"""
packed item batches need separate processing by overriding the relationship between
sales_invoice.py and packed_item.py`1

enhance:
- use stock_units for qty
"""

def get_row_batches(doc, cdt, row_item, current_item=None):
    """Returns a list of dictionaries with required batches for a given item or packed_item
        
        [{item_code, qty, batch, warehouse, actual_batch_qty}]

    :param doc - the doctype
    :param cdt - the child doctype
    :param row_item - the row to get required batches for
    :param parent_item - the parent row from items table in case of packed_item"""

    # Select only batches for this item from the entire batch list
    item_batches = filter_batches_by_item(row_item.item_code)

    if not item_batches:
        _print('no batches for given item_code', item_batches)
        frappe.msgprint(f"There are no valid batches for <strong>{row_item.item_code}</strong> in any warehouse. You can still save the invoice.")
        return
    total_required = 0
    if cdt == "items":
        row_qty_required = row_item.get("stock_qty") or row_item.get("transfer_qty") or row_item.get("qty") or 0
        reduced_batches, items_total_qty = deduct_prev_batches(doc, item_batches, cdt, row_item)    
        item_batches = reduced_batches
        #overall_qty_required = current_item.stock_qty + flt(items_total_qty)
        total_required = current_item.qty
            
        # Determine how many rows are needed for the given qty
        # If current has item batch - add: qty_required + item.qty
        rqd_rows = get_rqd_rows(item_batches, row_item, total_required)    
    else:
        if not row_item.item_code: return
    
        pi_qty_required = (flt(row_item.qty) * flt(current_item.stock_qty))
        total_required = pi_qty_required

        if current_item:
            # if items has batches belonging to this packed_item, modify the batches to be passed to packed_items
            reduced_batches, parent_qty_rqd = deduct_parent_qtys(doc, item_batches, current_item)    
            item_batches = reduced_batches
            #row_qty_required =  # + flt(parent_qty_rqd)
            #row_qty_required = current_item.stock_qty + flt(items_total_qty)
            rqd_rows = get_rqd_rows(item_batches, row_item, pi_qty_required)
            total_required = (flt(pi_qty_required)) # - flt(parent_qty_rqd))
            # Add rows with batch info for the given qty
            res = get_rows(item_batches, rqd_rows, total_required)
            return res


def deduct_parent_qtys(doc, item_batch_list, parent_item):
    """remove batches used in the parent items"""
    item_code = item_batch_list[0].item
    total_item_qty = 0
    copy_batch_list = filter_batches_by_item(item_code)
    count = 0

    all_items = doc.items + doc.packed_items
    
    for item in all_items:
        if item.item_code == item_code:
            # proceed if doc item_row is the same as the one in the batches
            print("deduct_parent_qtys",item.doctype,item.item_code, count)
            count+=1

            if item.batch_no and item.batch_no != "": #??
                # extract the item's dict
                batch_idx, batch =  get_batch_index_from_list(item_batch_list, item.batch_no, item.warehouse)
                #print("batch_idx, batch", batch_idx, batch  )
                if batch_idx==None:
                    print("")
                    print("continue")
                    continue
                else:
                    copy_batch_idx, copy_of_batch = get_batch_index_from_list(copy_batch_list, item.batch_no, item.warehouse)
                    original_qty = copy_of_batch.batch_qty
                    qty = batch.batch_qty - item.qty
                    print("")
                    print('qty = batch.batch_qty - item.qty', batch.batch_qty - item.qty, batch.name)
                    print("")

                    if qty < 1:
                        # delete the batch if its exhausted
                        print('delete',  item_batch_list[batch_idx] )
                        del item_batch_list[batch_idx]
                        print("")
                    else:
                        # reduce the batch if it still has stock
                        item_batch_list[batch_idx] = batch.update({"actual_batch_qty": original_qty })   
                        item_batch_list[batch_idx] = batch.update({"batch_qty": qty }) # reduces the batch qty
                    
                    total_item_qty += item.qty      
                    
                    #parent_batches.append(item_batch_list[item.batch_no])
                    """print("item ====================", item.item_code)
                    print("qty", qty)
                    print("original_qty", original_qty)
                    print("batch dict", batch)
                    print("total_item_qty ==========", total_item_qty)"""
    print("")
    print("end")
    print("total_item_qty", total_item_qty, "item_batch_list", item_batch_list)
    print("")
    return item_batch_list, total_item_qty


def deduct_parent_qtys_freeze(item_batch_list, items):
    """remove batches used in the parent items"""
    item_code = item_batch_list[0].item
    total_item_qty = 0
    copy_batch_list = filter_batches_by_item(item_code)
    
    for item in items:
        if item.item_code == item_code:
            # proceed if doc item_row is the same as the one in the batches
            if item.batch_no and item.batch_no != "": #??
                # extract the item's dict
                batch_idx, batch =  get_batch_index_from_list(item_batch_list, item.batch_no)
                if batch_idx==None:
                    continue
                else:
                    copy_batch_idx, copy_of_batch = get_batch_index_from_list(copy_batch_list, item.batch_no, item.warehouse)
                    original_qty = copy_of_batch.batch_qty
                    qty = batch.batch_qty - item.qty

                    if qty < 1:
                        del item_batch_list[batch_idx]
                    else:
                        item_batch_list[batch_idx] = batch.update({"actual_batch_qty": original_qty })   
                        item_batch_list[batch_idx] = batch.update({"batch_qty": qty })
                    
                    total_item_qty += item.qty      
                    
                    #parent_batches.append(item_batch_list[item.batch_no])
                    """print("item ====================", item.item_code)
                    print("qty", qty)
                    print("original_qty", original_qty)
                    print("batch dict", batch)
                    print("total_item_qty ==========", total_item_qty)

    print("item_batch_list, total_item_qty", total_item_qty)"""
    return item_batch_list, total_item_qty



def get_rows(item_batches, rqd_rows, total_req):
    if not item_batches:
        return

    assigned_qty = 0
    unassigned_qty = total_req
    row_data = []

    for idx in range(rqd_rows['rows']):
        if rqd_rows['rows'] == 1:
            row_data.append({
                'item_code': item_batches[idx].item,
                'qty': total_req, 
                'batch': item_batches[idx].name,
                'warehouse': item_batches[idx]['warehouse'],
                'actual_batch_qty': item_batches[idx].actual_batch_qty
            })
            _print("Only row", rqd_rows, idx, item_batches[idx]['name'], item_batches[idx]['batch_qty'], assigned_qty, unassigned_qty)

        else:
            if idx == 0:
                # First row
                assigned_qty = item_batches[idx]['batch_qty']
                unassigned_qty -= assigned_qty
                row_data.append({
                    'item_code': item_batches[idx].item,
                    'qty': assigned_qty, 
                    'batch': item_batches[idx].name,
                    'warehouse': item_batches[idx]['warehouse'],
                    'actual_batch_qty': item_batches[idx].actual_batch_qty
                })
                _print("First row", rqd_rows, idx, item_batches[idx].name, item_batches[idx]['batch_qty'], assigned_qty, unassigned_qty)
            else:
                if (idx + 1) == rqd_rows['rows']:
                    # Last batch
                    _print("Last 1", rqd_rows, idx, item_batches[idx].name, item_batches[idx]['batch_qty'], assigned_qty, unassigned_qty)

                    if unassigned_qty > item_batches[idx]['batch_qty']:
                        
                        row_data.append({
                            'item_code': item_batches[idx].item,
                            'qty': item_batches[idx]['batch_qty'], 
                            'batch': item_batches[idx].name,
                            'warehouse': item_batches[idx]['warehouse'],
                            'actual_batch_qty': item_batches[idx].actual_batch_qty
                        })

                        assigned_qty += item_batches[idx]['batch_qty']
                        unassigned_qty -= item_batches[idx]['batch_qty']

                        row_data.append({
                            'item_code': item_batches[idx].item,
                            'qty': unassigned_qty, 
                            'batch': item_batches[idx].name,
                            'warehouse': item_batches[idx]['warehouse'],
                            'actual_batch_qty': item_batches[idx].actual_batch_qty
                        })
                        
                        assigned_qty += unassigned_qty
                        unassigned_qty -= unassigned_qty

                        _print("Last 2", rqd_rows, idx, item_batches[idx].name, item_batches[idx]['batch_qty'], assigned_qty, unassigned_qty)
                    else:
                        row_data.append({
                            'item_code': item_batches[idx].item,
                            'qty': unassigned_qty, 
                            'batch': item_batches[idx].name,
                            'warehouse': item_batches[idx]['warehouse'],
                            'actual_batch_qty': item_batches[idx].actual_batch_qty
                        })
                        assigned_qty += unassigned_qty
                        unassigned_qty -= unassigned_qty

                        _print("Last 3", rqd_rows, idx, item_batches[idx].name, item_batches[idx]['batch_qty'], assigned_qty, unassigned_qty)

                    _print("After last", rqd_rows, idx, item_batches[idx].name, item_batches[idx]['batch_qty'], assigned_qty, unassigned_qty)
                else:
                    # Mid batches
                    assigned_qty += item_batches[idx]['batch_qty']
                    unassigned_qty -= item_batches[idx]['batch_qty']
                    row_data.append({
                        'item_code': item_batches[idx].item,
                        'qty': item_batches[idx]['batch_qty'], 
                        'batch': item_batches[idx].name,
                        'warehouse': item_batches[idx]['warehouse'],
                        'actual_batch_qty': item_batches[idx].actual_batch_qty
                    })
                    _print("Mid batches", rqd_rows, idx, item_batches[idx].name, item_batches[idx]['batch_qty'], assigned_qty, unassigned_qty)
        
        batch_dict =  get_list_dict_by_key(row_data, 'qty', 0)
        if batch_dict:
            del row_data[row_data.index(batch_dict)]

    return row_data



def get_batch_index_from_list(batch_list, batch_no, warehouse=None):
    """Get a single batch from the list based on its name or number."""
    if warehouse:
        batch_dict =  get_list_dict_by_key(batch_list, 'name', batch_no, 'warehouse', warehouse)
    else:
        batch_dict =  get_list_dict_by_key(batch_list, 'name', batch_no)

    if batch_dict:
        return batch_list.index(batch_dict), batch_dict
    return None, None

    # extract the item's batch using its name and index                
    index = item_batch_list.index(batch_dict)
    batch = item_batch_list[index]

    original_qty = copy_batch_list[copy_batch_list.index(batch_dict)].batch_qty


def deduct_prev_batches(doc, item_batch_list, current_item):
    """Removes previously used batches from batch_list
    
    :param doc - the document
    :param item_batch_list - the list of available batches to be selected
    :param cdt - the name of the field for child doctype
    :param current_item - the current row being processed"""

    item_code = current_item.item_code
    total_item_qty = current_item.qty
    required = 0
    count=0

    copy_batch_list = filter_batches_by_item(item_code)
    
    for item in doc.items:
        if current_item.name == item.name:
            # skip the current item
            continue
        
        if item.item_code == item_code:
            # proceed if doc item_row is the same as the one in the batches

            print("deduct_prev count", count)
            count+=1
            if item.batch_no and item.batch_no != "": # no batch??
                # extract the item's dict

                #for batch in item_batch_list:

                batch_idx, batch = get_batch_index_from_list(item_batch_list, item.batch_no, item.warehouse)
                
                if batch_idx==None:
                    continue
                else:

                    copy_batch_idx, copy_of_batch = get_batch_index_from_list(copy_batch_list, item.batch_no, item.warehouse)
                    original_qty = copy_of_batch.batch_qty

                    qty = batch.batch_qty - item.qty
                    required += item.qty

                    if qty < 0:
                        # if batch or left over has less qty than item
                        total_item_qty += batch.batch_qty
                        # deduct batch_qty only and proceed to next batch
                        print('# batch fully used, proceed to next batch', batch.name, 'required', required, 'total_item_qty', total_item_qty)
                        
                        del item_batch_list[batch_idx]
                        
                        #continue # to next batch

                    elif qty == 0:
                        # if batch has exact qty
                        total_item_qty += item.qty
                        print('batch was fully used', batch.name, 'required', required, 'total_item_qty', total_item_qty)
                        
                        del item_batch_list[batch_idx]

                        if required == total_item_qty:
                            print('break', 'cont')
                            #break
                            #break
                        else:
                            print('continue')
                            #continue

                    elif qty > 0:
                        # if batch has surplus qty
                        total_item_qty += item.qty
                        print('batch has balance', batch.name, 'required', required, 'total_item_qty', total_item_qty)
                        
                        item_batch_list[batch_idx] = batch.update({"actual_batch_qty": original_qty })   
                        item_batch_list[batch_idx] = batch.update({"batch_qty": qty })
                        #break
                    
                    # total_item_qty += item.qty 
                #parent_batches.append(item_batch_list[item.batch_no])
                """print("")
                print("item ====================", item.item_code)
                print("")
                print("qty", qty, "original_qty", original_qty, "item.qty", item.qty, "required", required, "total_item_qty", total_item_qty)
                print("")"""
                #print("batch dict", batch)
                

    #print("total_item_qty", total_item_qty, "item_batch_list", item_batch_list)
    return item_batch_list, total_item_qty

def filter_given_batches_by_item(batches, item):
    # batches dictionary is defined globally
    
    item_batches = []
    for batch in batches:
        if batch.item == item:
            item_batches.append(batch)
    return item_batches

def set_batch_nos(doc, warehouse_field, throw=False, child_table="items"):
    """Automatically select `batch_no` for outgoing items in item table"""
    
    #print("")
    #print("-------------------------------------------------", child_table)
    #print("")

    count = 0
    row_batches = []
    item_batches = []
    batches = get_batches()
    local_batches = batches['batches'] # gives duplicate batches w/o deleting used ones
    #local_batches = batches['batches']

    child_rows = doc.get(child_table)
    child_rows_copy = child_rows.copy()
    batch = {}
    

    for d in child_rows_copy:      
        qty = d.get("stock_qty") or d.get("transfer_qty") or d.get("qty") or 0
        warehouse = d.get(warehouse_field, None)

        has_batch_no = item_has_batch_no(batches, d.item_code)
        
        if qty > 0 and (has_batch_no and has_batch_no==1):

            #print("")
            #print("---------------------------", d.item_code, count)
            count+=1
            #print("")

            item_batches = filter_given_batches_by_item(local_batches, d.item_code)
            #bug
            if not item_batches:
                print('no batches for given item_code', item_batches)
                frappe.msgprint(
                    _(
                        "Row #{0}: There are no valid batches for <strong>{1}</strong> in any warehouse. You can still save the invoice."
                    ).format(d.idx, frappe.bold(d.item_code))
                )
                return
            
            if d.batch_no:
                batch_idx, batch = get_batch_index_from_list(item_batches, d.batch_no, d.warehouse)

                # check if the batch has enough qty and leave it if so
                if batch and d.qty <= batch.batch_qty:
                    continue

            current_batches = deduct_prev_batches(doc, item_batches, d)            
            reqd_rows = get_rqd_rows(current_batches[0], d.item_code, d.qty)
            

            #print('reqd_rows', reqd_rows)
            #print('')
            
            row_batches = get_rows(current_batches[0], reqd_rows, d.qty)
            if row_batches:
                insert_batch_rows(doc, child_table, row_batches, row=d)
    
            #local_batches = current_batches[0]
            
    for r in child_rows:
        # batch qty validation

        if r.batch_no:
            if not batch:
                batch_idx, batch = get_batch_index_from_list(item_batches, r.batch_no, r.warehouse)
                
            batch_qty = get_batch_qty(batch_no=r.batch_no, warehouse=r.warehouse, item_code=r.item_code)
            
            prev_item = {}
            msg = _("Row #{0}: The batch {1} only has {2} qty. {3} qty is needed, no other warehouses can satisfy the requirement either. Save the invoice and produce {3} or more to submit it."
                    ).format(r.idx, frappe.bold(r.batch_no), frappe.bold(batch_qty), frappe.bold(r.qty))
            
            # get prev item if the given row isnt the first row in the list
            if r.idx !=1:
                prev_item = get_list_dict_by_key(child_rows, 'idx', r.idx - 1)

                if prev_item.batch_no == r.batch_no:
                    msg = _(
                            "The Qty in Row #{0} was split from Row #{1} after running out of {2} in all other warehouses and batches. You can proceed to save the Invoice."
                        ).format(r.idx, r.idx -1, frappe.bold(r.item_name), frappe.bold(r.batch_no), frappe.bold(batch_qty), frappe.bold(r.qty))
            
            if flt(batch_qty) < flt(r.qty):
                frappe.msgprint(
                    msg
                )

    #print("------------------------------------------------ all items done")

def insert_batch_rows(doc, child_table, row_batches, row):
    #print("insert_batch_rows - row_batches", row_batches)
    count = 0
    
    for batch in row_batches:
        if count==0:                
            row.batch_no = batch.get('batch')
            row.warehouse = batch.get('warehouse')
            row.qty = batch.get('qty')
            row.base_rate = row.base_rate
            row.base_amount = row.base_rate * batch.get('qty')
            row.amount = row.rate * batch.get('qty')
            row.rate = row.rate
        else:
        
            fields = {
                'item_code': row.item_code,
                'rate': row.rate,
                'item_name': row.item_name,
                'description': row.description,
                'uom': row.uom,
                'qty': batch.get('qty'),
                'batch_no': batch.get('batch'),
                'warehouse': batch.get('warehouse'),
            }
            
            if child_table == "items":
                fields.update({
                    'income_account': row.income_account,
                    'conversion_factor': row.conversion_factor,
                    'base_rate': row.base_rate,
                    'base_amount': row.base_rate * batch.get('qty'),
                    'amount': row.rate * batch.get('qty'),
                    'expense_account': row.expense_account,
                    'discount_account': row.discount_account,
                    'cost_center': row.cost_center,
                })
            elif child_table == "packed_items":  
                fields.update({      
                    'parent_item': row.parent_item,
                    'parent_detail_docname': row.parent_detail_docname,
                })

            doc.append(child_table, fields)
        count+=1


def get_list_dict_by_key(data_list, key, value, key2=None, val2=None):
    for row in data_list:
        if row.get(key) == value:
            if key2 is None or row.get(key2) == val2:
                return row
    return None

def filter_batches_by_item(item):
    # batches dictionary is defined globally
    batches = get_batches()
    item_batches = []
    for batch in batches['batches']:
        if batch.item == item:
            item_batches.append(batch)
    return item_batches

def get_rqd_rows(item_batches, row_item, qty_still_required):
    
    rows_needed = 0
    max_batch_qty = 0

    for batch in item_batches:
        max_batch_qty += batch['batch_qty']

        if qty_still_required > batch['batch_qty']:
            qty_still_required -= batch['batch_qty']
            rows_needed += 1
        else:
            rows_needed += 1
            break

    return {
            'rows': rows_needed,
            'max_batch_qty': max_batch_qty
        }


@frappe.whitelist()
def get_warehouse(item_code):
    warehouses = frappe.get_all(
        'Bin',
        filters={
            'item_code': item_code,
            'actual_qty': ['>', 0]
        },
        fields=['item_code', 'warehouse', 'actual_qty', 'stock_uom']
    )

    return warehouses

class UnableToSelectBatchError(frappe.ValidationError):
    pass

@frappe.whitelist()
def get_single_batch_no(item_code, warehouse=None, qty=1, throw=False, serial_no=None):
    """
    Get batch number using First Expiring First Out method.
    :param item_code: `item_code` of Item Document
    :param warehouse: name of Warehouse to check
    :param qty: quantity of Items
    :return: String represent batch number of batch with sufficient quantity else an empty String
    """
    
    batch_no = None
    this_warehouse = None
    batches = filter_batches_by_item(item_code)
    
    #print(batches)
    for batch in batches:
        #print(qty, flt(qty) <= flt(batch.batch_qty), batch)
        if flt(qty) <= flt(batch.batch_qty):
            batch_no = batch.name
            this_warehouse = batch.warehouse
            break

    if not batch_no:
        frappe.msgprint(
            _(
                "Please select a Batch for Item {0}. Unable to find a single batch that fulfills this requirement in any warehouse."
            ).format(frappe.bold(item_code)), console=True
        )
        if throw:
            raise UnableToSelectBatchError
    if warehouse != None:
        return batch_no
    return [batch_no, this_warehouse]

@frappe.whitelist()
def get_batch_no(item_code, qty=1, throw=False, serial_no=None):
    """
    Get batch number using First Expiring First Out method.
    :param item_code: `item_code` of Item Document
    :param warehouse: name of Warehouse to check
    :param qty: quantity of Items
    :return: String represent batch number of batch with sufficient quantity else an empty String
    """
    
    batch_no = None
    warehouse = None
    batches = filter_batches_by_item(item_code)
    
    #print(batches)
    for batch in batches:
        #print(qty, flt(qty) <= flt(batch.batch_qty), batch)
        if flt(qty) <= flt(batch.batch_qty):
            batch_no = batch.name
            warehouse = batch.warehouse
            break

    """if not batch_no:
        frappe.msgprint(
            _(
                "Please select a Batch for Item {0}. Unable to find a single batch that fulfills this requirement"
            ).format(frappe.bold(item_code))
        )
        if throw:
            raise UnableToSelectBatchError"""

    return batch_no, warehouse
    

def item_has_batch_no(batches, item_code):
    """Returns `1` if `item.batch_no = 1`, else returns false.

    :param item_code - the item code to be checked"""
    items = batches['items']

    has_batch_no = get_list_dict_by_key(items, 'item_code', item_code)
    if has_batch_no:
        return has_batch_no.has_batch_no
    return None



@frappe.whitelist()
def get_batch_qty(
    batch_no=None, warehouse=None, item_code=None, posting_date=None, posting_time=None
):
    """Returns batch actual qty if warehouse is passed,
            or returns dict of qty by warehouse if warehouse is None

    The user must pass either batch_no or batch_no + warehouse or item_code + warehouse

    :param batch_no: Optional - give qty for this batch no
    :param warehouse: Optional - give qty for this warehouse
    :param item_code: Optional - give qty for this item"""

    sle = frappe.qb.DocType("Stock Ledger Entry")

    out = 0
    if batch_no and warehouse:
        query = (
            frappe.qb.from_(sle)
            .select(Sum(sle.actual_qty))
            .where((sle.is_cancelled == 0) & (sle.warehouse == warehouse) & (sle.batch_no == batch_no))
        )

        if posting_date:
            if posting_time is None:
                posting_time = nowtime()

            query = query.where(
                CombineDatetime(sle.posting_date, sle.posting_time)
                <= CombineDatetime(posting_date, posting_time)
            )

        out = query.run(as_list=True)[0][0] or 0

    if batch_no and not warehouse:
        out = (
            frappe.qb.from_(sle)
            .select(sle.warehouse, Sum(sle.actual_qty).as_("qty"))
            .where((sle.is_cancelled == 0) & (sle.batch_no == batch_no))
            .groupby(sle.warehouse)
        ).run(as_dict=True)

    if not batch_no and item_code and warehouse:
        out = (
            frappe.qb.from_(sle)
            .select(sle.batch_no, Sum(sle.actual_qty).as_("qty"))
            .where((sle.is_cancelled == 0) & (sle.item_code == item_code) & (sle.warehouse == warehouse))
            .groupby(sle.batch_no)
        ).run(as_dict=True)

    return out
