def get_last_payment_columns():
    config_list = list()
    config_list.append(("A", "Ciudad", 'city'))
    config_list.append(("B", "Cliente", 'customer'))
    config_list.append(("C", "Dirección", 'address'))
    config_list.append(("D", "Última Cobranza", 'lastcollection'))
    config_list.append(("E", "Motivo", 'reason'))
    return config_list