def required_inputs():
    return [
        {
            "name": "email_address",
            "description": "An example of how to list required input",
            "type": "String"
        }
    ]

def optional_inputs():
    return [
        {
            "name": "optional_input_example",
            "description": "An example of how to list optional input",
            "type": "String"
        }
    ]

def output():
    """
    'name' is required, should be lowercase alphanumeric and _
    'type' is required, see https://docs.demyst.com/apis/gateway/types/ for acceptable type values.
    """
    return [
        {
            "name": "output_field_example",
            "type": "String",
            "description": "An example of how to list the outputs of the data function",
            "sample": "blue"
        }
    ]

def metadata():
    return {
        "create_provider": True,
        "category": "Finance",
        "data_provider_name": "Provider name",
        "data_product_name": "Data Function Name",
        "data_product_description": "Purpose of the data function, when to use, what it provides",
        "beta": True,
        "price_final": True,
        "fcra": False,
        "region": "us",
        "data_provider_website": "www.example.com"
    }

def tile_data():
    result_dict = {}
    result_dict.update(metadata())
    result_dict.update({'optional_inputs': optional_inputs()})
    result_dict.update({'required_inputs': required_inputs()})
    result_dict.update({'output': output()})
    return result_dict
