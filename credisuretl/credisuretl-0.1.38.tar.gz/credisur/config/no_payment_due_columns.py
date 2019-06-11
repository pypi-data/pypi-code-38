def get_no_payment_due_columns():
    config_list = list()
    config_list.append(("A", "Ciudad", 'city'))
    config_list.append(("B", "Cliente", 'customer'))
    config_list.append(("C", "Orden de Compra", 'sales_order'))
    config_list.append(("D", "Dirección", 'address'))
    config_list.append(("E", "Monto Vencido", 'past_due_debt'))
    config_list.append(("F", "Monto Cobrado", 'paid_amount'))
    config_list.append(("G", "Primer Vencimiento", 'due_date'))
    config_list.append(("H", "Código", 'raw_code'))
    return config_list

'''
"%s - %s (orden: %s) - %s. Monto vencido: %s. Monto cobrado: %s. Primer vencimiento: %s" % (

    "city": self.city,
"customer": self.customer,
"sales_order": self.sales_order,
"adddress": self.address or 'Sin dirección',
"past_due_debt": self.past_due_debt,
"paid_amount": self.paid_amount,
"due_date": self.due_date.strftime("%d/%m/%Y")
'''