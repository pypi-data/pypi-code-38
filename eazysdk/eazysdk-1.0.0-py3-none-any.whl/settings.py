class Settings:
    current_environment = {
        'env': 'sandbox'    # sandbox || ecm3
    }

    sandbox_client_details = {
        'client_code': 'SDKTST',
        'api_key': 'hkZujzFR2907XAtYe6qkKRsBo',
    }

    ecm3_client_details = {
        'client_code': 'LUISCT',
        'api_key': 'xAQdXTPtZPG3QqsUJw73wx1o',
    }



    # Changing these values without prior discussion with EazyCollect may
    # lead to unintended behaviour. If in doubt, contact EazyCollect.
    direct_debit_processing_days = {
        'initial': 10,
        'ongoing': 5,
    }

    contracts = {
        'auto_start_date': False,
        'auto_fix_ad_hoc_termination_type': False,
        'auto_fix_ad_hoc_at_the_end': False,
        'auto_fix_payment_day_in_month': False,
        'auto_fix_payment_month_in_year': False,
    }

    payments = {
        'auto_fix_payment_date': False,
        'is_credit_allowed': False,
    }

    warnings = {
        'customer_search': True,
    }

    other = {
        'bank_holidays_update_days': 30,
        'force_schedule_updates': False,
    }
