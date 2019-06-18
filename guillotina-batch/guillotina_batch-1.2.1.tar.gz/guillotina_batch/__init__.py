from guillotina import configure


app_settings = {
    'max_batch_size': 200
}


def includeme(root):
    """
    custom application initialization here
    """
    configure.scan('guillotina_batch.api')
