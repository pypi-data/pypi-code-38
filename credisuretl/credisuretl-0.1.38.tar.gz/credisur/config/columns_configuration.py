def get_columns_configuration():
    config_list = list()
    config_list.append(("A", "Ciudad", 'city'))
    config_list.append(("B", "Cliente", 'customer'))
    config_list.append(("C", "Dirección", 'address'))
    config_list.append(("D", "Teléfono", 'phone'))

    config_list.append(("E", "Fecha de Compra", 'date_of_purchase'))
    config_list.append(("F", "Fecha de Vencimiento", 'due_date'))

    config_list.append(("G", "Orden de Compra", 'order'))
    config_list.append(("H", "Última Cobranza", 'last_collection'))

    config_list.append(("I", "Cuotas", 'plan'))

    config_list.append(("J", "Cuotas a pagar", 'current_payment'))
    config_list.append(("K", "Valor de cuota", 'payment'))

    config_list.append(("L", "Monto total a cobrar", 'amount_to_collect'))
    config_list.append(("M", "Descripción", 'full_description'))
    config_list.append(("N", "Versión", 'version'))
    return config_list