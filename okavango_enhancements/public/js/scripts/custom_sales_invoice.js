// disable batch dialog in
// apps/erpnext/erpnext/public/js/controllers/transaction.js
// by changing show_batch_dialog = update_stock;
// to show_batch_dialog = 0;

///apps/erpnext/erpnext/stock/doctype/batch/batch.py
// add return to get_batch_no


var batches = [];
var items = [];

frappe.ui.form.on('Sales Invoice', {
    /**onload: function(frm){
         testing
        frm.set_value('customer', "Wally Ng'andu");
        frm.set_value('service_type', "Boxes");
        return;
        
        // set bactches fetched through the server
        // modified to include warehouse batch is fetched from
        frappe.call({
    		method: 'okavango_enhancements.app.get_batches',
    		callback: (r) => {
    		    batches = r.message.batches;
    		    items = r.message.items;
    		}
    	});
    },
    
    */
    //wh selector
    validate: function (frm) {
        validate_pi_warehouse_to_qtys(frm);
    },
    after_save: function (frm) {
        //return;
        validate_pi_warehouse_to_qtys(frm);
    }
    
});

frappe.ui.form.on('Sales Invoice Item',{
    /**qty:function(frm, cdt, cdn) {return;
        log('qty');
        process_row_batches(frm, cdt, cdn);
    },
    item_code:function(frm, cdt, cdn){return;
        log('item_code');
        process_row_batches(frm, cdt, cdn);
    }
    */
});


//This function takes a row as input and checks if the item_code of the given row is unique among its peers
function row_is_unique(row) {
    var itemCode = row.item_code;
    var rowCount = cur_frm.doc.packed_items.length;
    var duplicateCount = 0;

    for (var i = 0; i < rowCount; i++) {
        var currentRow = cur_frm.doc.packed_items[i];
        if (currentRow.item_code === itemCode) {
            duplicateCount++;
            if (duplicateCount > 1) {
                return false;
            }
        }
    }

    return true;
}

function get_warehouse_for_row(row) {
    return new Promise(function (resolve, reject) {
        frappe.call({
            method: 'okavango_enhancements.app.get_warehouse',
            args: {
                item_code: row.item_code,
            },
            callback: function (r) {
                if (r.message && r.message.length > 0) {
                    resolve(r.message);
                } else {
                    reject();
                }
            },
        });
    });
}

function update_warehouse_description(dialog, warehouses, row) {
    var selectedWarehouse = dialog.get_value('warehouse');
    if (selectedWarehouse) {
        var warehouseInfo = warehouses.find((wh) => wh.warehouse === selectedWarehouse);
        var description = `${warehouseInfo.warehouse} (${warehouseInfo.actual_qty} ${warehouseInfo.stock_uom})`;
        dialog.fields_dict['warehouse'].set_description(description);
    } else {
        dialog.fields_dict['warehouse'].set_description('');
    }
}

function validate_pi_warehouse_to_qtys(frm) {
    var promises = [];
    if(cur_frm.doc.packed_items === undefined || !cur_frm.doc.packed_items){
        return;
    }
    

    cur_frm.doc.packed_items.forEach(function (row) {
        if (row.qty > row.actual_qty && (row.batch_no===undefined || !row.batch_no)){
            promises.push(get_warehouse_for_row(row));
        }
    });
    Promise.all(promises)
        .then(function (results) {
            var index = 0;
            cur_frm.doc.packed_items.forEach(function (row) {
                if (row.qty > row.actual_qty && (row.batch_no===undefined || !row.batch_no)) {
                    var warehouses = results[index];
                    let row_qty = locals[row.doctype][row.name].qty;
                    
                    var dialog = new frappe.ui.Dialog({
                        title: __('Pick a Warehouse for Packed Item #' + row.idx +': '+ row.item_code),
                        fields: [
                            {
                                fieldname: 'qty',
                                label: __('Quantity Required'),
                                fieldtype: 'Data',
                                read_only: 1,
                                default: row_qty + ' ' + row.uom,
                            },
                            {
                                fieldname: 'warehouse',
                                label: __('Warehouse'),
                                fieldtype: 'Link',
                                options: 'Warehouse',
                                default: warehouses[0].warehouse,
                                reqd: 1,
                                get_query: function () {
                                    return {
                                        filters: {
                                            name: ['in', warehouses.map((wh) => wh.warehouse)],
                                        },
                                    };
                                },
                            },
                        ],
                        primary_action: function () {
                            var values = dialog.get_values();
                            if (values) {
                                frappe.model.set_value(row.doctype, row.name, 'warehouse', values.warehouse);
                                dialog.hide();
                            }
                        },
                        primary_action_label: __('Update Warehouse'),
                    });

                    // Update warehouse description on change
                    dialog.fields_dict['warehouse'].change = function () {
                        update_warehouse_description(dialog, warehouses, row);
                    };

                    update_warehouse_description(dialog, warehouses, row);

                    dialog.show();
                    index++;
                }
            });
        })
        .catch(function () {
           // frappe.msgprint(__('Sorry, some items are out of stock in all warehouses.'));
        });
}


function get_item_batches(batches, item){
    let i = 0;
    let item_batches = [];

    for (let idx in batches) {
        if (batches[idx].item === item){
            item_batches.push(batches[idx]);
        }
    }
    return item_batches;
}

// determine how many rows needed for given qty
function get_rqd_rows(item_batches, row){
    // Samosa Chicken - 6
    // b1 - 1 - 5
    // b2 - 5 - 0
    // b3 - 469
    // 5 returns 2, 10 returns 3, 1M returns the max that can be satisfied
    
    let qty_still_required = row.qty; // Initialize to the total quantity needed
    let rows_needed = 0;
    let max_batch_qty = 0;

    for (let idx in item_batches) {
        max_batch_qtyp += item_batches[idx].batch_qty;

        // Check if the quantity still required is greater than the current batch quantity
        if (qty_still_required > item_batches[idx].batch_qty) {
            qty_still_required -= item_batches[idx].batch_qty;
            rows_needed++;
        } else {
            // If the remaining quantity is less than or equal to the current batch, we have found the required number of rows
            rows_needed++;
            break;
        }
    }

    return {
        rows: rows_needed,
        max_batch_qty: max_batch_qty
    };
    
}

function get_list_dict_by_key(data_list, key, value) {
    for (let i = 0; i < data_list.length; i++) {
        const row = data_list[i];
        if (row[key] === value) {
            return row;
        }
    }
    return false;
}

function process_row_batches(frm, cdt, cdn){return;
    const row = locals[cdt][cdn];
    
	// validate item is set and the given qty
    if(!row.item_code || row.item_code === undefined || row.qty < 0){ 
        console.log('!row.item_code || row.item_code === undefined || row.qty < 0');
        return;
    }
    
    // validate if its a batch item before proceeding
    const is_batch_item = get_list_dict_by_key(items, 'item_code', row.item_code);

    if (is_batch_item.has_batch_no !== 1) {
        console.log('has no batch_no', is_batch_item);
        return;
    }
    
    // select only batches for this item from entire batch list
    let item_batches = get_item_batches(batches, row.item_code);
    
    if (item_batches.length === 0){
        console.log('no batches', item_batches);
        frappe.msgprint({
            message: __(`There are no valid batches for <strong>${row.item_code}</strong> in any warehouse.<br/>You can still save the invoice.`),
            title: __('Warning: No Stock'),
            indicator: 'red'
        });
    }
    add_rows(item_batches, row, frm, cdt, cdn);
}

function add_rows(item_batches, row, frm, cdt, cdn) {
    if (item_batches.length === 0){
        return;
    }
    // Determine how many rows are needed for the given qty
    let rqd_rows = get_rqd_rows(item_batches, row);

    let total_req = row.qty;
    let assigned_qty = 0;
    let unassigned_qty = total_req;
    // console.table(item_batches);

    for (let idx = 0; idx < rqd_rows.rows; idx++) {
        // Breakdown initial row.qty
        // Spread it across new rows and assign batches to each
        //   1. Reduce item to qty in batch and assign that as the qty
        //   2. Repeat until qty is satisfied
        
        if (rqd_rows.rows === 1) {
            // If only one batch is needed, select it and that's it!
            frappe.model.set_value(cdt, cdn, 'batch_no', item_batches[0].name);
            frm.set_value('set_warehouse', item_batches[0].warehouse);
            
            frappe.model.set_value(cdt, cdn, 'warehouse', item_batches[0].warehouse);
            console.log("Only row", rqd_rows, idx, item_batches[idx].batch_qty, item_batches[0].warehouse);
        } else {
            if (idx === 0) {
                // First row
                assigned_qty = item_batches[idx].batch_qty;
                unassigned_qty -= assigned_qty;
                
                row.qty = item_batches[idx].batch_qty;
                row.batch_no = item_batches[idx].name;
                row.warehouse = item_batches[idx].warehouse;
                console.log("First row", rqd_rows, idx, item_batches[idx].batch_qty, assigned_qty, unassigned_qty);
            } 
            else {
                if (idx + 1 === rqd_rows.rows) {
                    
                    // Last batch
                    // if greater than last batch_qty, split
                    // assign batchqty and difference to new row
                    console.log("Last 1", rqd_rows, idx, item_batches[idx].batch_qty, assigned_qty, unassigned_qty);
                    
                    if (unassigned_qty > item_batches[idx].batch_qty) {
                        insert_row(frm, row, item_batches[idx].batch_qty, item_batches[idx]); 
                        
                        assigned_qty += item_batches[idx].batch_qty;
                        unassigned_qty -= item_batches[idx].batch_qty;
                        
                        insert_row(frm, row, unassigned_qty, item_batches[idx]);
                        
                        assigned_qty += unassigned_qty;
                        unassigned_qty -= unassigned_qty;
                        
                        console.log("Last 2", rqd_rows, idx, item_batches[idx].batch_qty, assigned_qty, unassigned_qty);
                    }
                    else {
                        insert_row(frm, row, unassigned_qty, item_batches[idx]);
                        assigned_qty += unassigned_qty;
                        unassigned_qty -= unassigned_qty;
                        
                        console.log("Last 3", rqd_rows, idx, item_batches[idx].batch_qty, assigned_qty, unassigned_qty);
                    }
                    console.log("After last", rqd_rows, idx, item_batches[idx].batch_qty, assigned_qty, unassigned_qty);
                } 
                else {
                    
                    // Mid batches
                    assigned_qty += item_batches[idx].batch_qty;
                    unassigned_qty -= item_batches[idx].batch_qty;
                    insert_row(frm, row, item_batches[idx].batch_qty, item_batches[idx]);
                    console.log("Mid batches", rqd_rows, idx, item_batches[idx].batch_qty, assigned_qty, unassigned_qty);
                }
            }
        }
    }
    
    frm.refresh_field(row.parentfield);
}

function log(...args){
    const formattedArgs = args.map((arg) => {
        return typeof arg === "object" ? JSON.stringify(arg) : arg;
    });

  console.log(...formattedArgs);
}

function insert_row(frm, row, qty, batch){
    
    if(row.doctype==="Sales Invoice Item"){
    
        frm.add_child('items', {
            item_code: row.item_code,
            rate: row.rate,
            item_name: row.item_name,
            description: row.description,
            income_account: row.income_account,
            expense_account: row.expense_account,
            discount_account: row.discount_account,
            cost_center: row.cost_center,
            uom: row.uom,
            qty: qty,
            batch_no: batch.name,
            warehouse: batch.warehouse,
            
        });  
    }
    else {
        frm.add_child(row.parentfield, {
            parent_item: row.parent_item,
            item_code: row.item_code,
            rate: row.rate,
            item_name: row.item_name,
            description: row.description,
            parent_detail_docname: row.parent_detail_docname,
            uom: row.uom,
            qty: qty,
            batch_no: batch.name,
            warehouse: batch.warehouse,
            
        }); 
    }
    return;
}

    
    // What if
    //  - no more batches to assign to item qty?
    //      - assign last batch and remaining qty to last row - d
    //  - there are no batches? 
    //      - tell the user
    //  - qty changes - it increments
    //  - adding other items - np
    //. - existing batches?????
    //      - check existing and leave them if batch_qty => row.qty
    //  - item batches split across whs? - np
