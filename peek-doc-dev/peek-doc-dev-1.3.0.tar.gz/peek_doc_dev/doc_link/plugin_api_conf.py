

def load(createApiDocsFunc):
    """ Load
        
        Create APIs with the AutoAPI hack above
    """


    import peek_plugin_data_dms
    createApiDocsFunc(peek_plugin_data_dms.__file__)
    

    import peek_core_device
    createApiDocsFunc(peek_core_device.__file__)
    

    import peek_plugin_diagram
    createApiDocsFunc(peek_plugin_diagram.__file__)
    

    import peek_plugin_docdb
    createApiDocsFunc(peek_plugin_docdb.__file__)
    

    import peek_core_email
    createApiDocsFunc(peek_core_email.__file__)
    

    import peek_plugin_graphdb
    createApiDocsFunc(peek_plugin_graphdb.__file__)
    

    import peek_plugin_livedb
    createApiDocsFunc(peek_plugin_livedb.__file__)
    

    import peek_plugin_user
    createApiDocsFunc(peek_plugin_user.__file__)
    

    import peek_plugin_search
    createApiDocsFunc(peek_plugin_search.__file__)
    
