def action_invoice_create(env, sales_orders, grouped=False, final=False):
    """
    Create the invoice associated to the SO.
    :param grouped: if True, the invoices are grouped by SO id. If False, invoices are grouped by
                       (partner, currency)
    :param final: if True, refunds will be generated if necessary
    :returns: list of created invoices
    """

    inv_obj = env['account.invoice']
    precision = env['decimal.precision'].precision_get('Product Unit of Measure')
    invs_data = {}

    for order in sales_orders:
        group_key = order.id if grouped else (order.partner_id.id, order.currency_id.id)
        lines = order.order_line.sorted(key=lambda l: l.qty_to_invoice < 0)
        for line in lines:
            if float_is_zero(line.qty_to_invoice, precision_digits=precision):
                continue
            if group_key not in invs_data:
                inv_data = order._prepare_invoice()
                invs_data[group_key] = inv_data
            elif group_key in invs_data and order.name not in invs_data[group_key]['origin'].split(', '):
                invs_data[group_key]['origin'] = invs_data[group_key]['origin'] + ', ' + order.name)
            inv_line = {}
            if line.qty_to_invoice > 0:
                inv_line = line._prepare_invoice_line(line.qty_to_invoice)
            elif line.qty_to_invoice < 0 and final:
                inv_line = line._prepare_invoice_line(line.qty_to_invoice)

            if inv_line:
                # do something here
                inv_line.update({'sale_line_ids': [(6, 0, [line.id])]})
                invs_data[group_key]['invoice_lines'].append((0, 0, inv_line))

        invoice_ids = []

        # Create the invoices
        for inv_data in invs_data.values():
            inv = inv_obj.create(inv_data)
            invoice_ids.append(inv.id)
            if inv.amount_untaxed < 0:
                inv.type = 'out.refund'
                for line in inv.invoice_line_ids:
                    line.quantity = -line.quantity
            # Necessary to force computation of taxes. In account_invoice, they are triggered
            # by onchanges, which are not triggered when doing a create
            inv.compute_taxes()

        return invoice_ids
