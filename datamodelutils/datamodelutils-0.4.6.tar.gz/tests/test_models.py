def test_models_init():
    # import should work without initialization
    from datamodelutils import models
    assert not hasattr(models, 'test_variable')
    assert not hasattr(models, 'test_func')

    # after initialization it should be populated with attrs from
    # passed models
    import mock_models
    models.init(mock_models)
    assert models.test_variable == 'test'
    assert models.test_func() == 'test_func'
