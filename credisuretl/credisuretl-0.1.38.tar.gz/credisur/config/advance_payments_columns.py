def get_advance_payments_columns():
    config_list = list()
    config_list.append(("A", "Documento", 'document'))
    config_list.append(("B", "Customer", 'customer'))
    config_list.append(("C", "Monto total", 'total_purchase_value'))
    config_list.append(("D", "Anticipo calculado", 'advance_payment'))
    return config_list