from edc_reference import ReferenceModelConfig, site_reference_configs


def register_to_site_reference_configs():
    site_reference_configs.registry = {}

    reference = ReferenceModelConfig(name="data_manager_app.CrfOne", fields=["f1"])
    site_reference_configs.register(reference)

    reference = ReferenceModelConfig(name="data_manager_app.CrfTwo", fields=["f1"])
    site_reference_configs.register(reference)

    reference = ReferenceModelConfig(name="data_manager_app.CrfThree", fields=["f1"])
    site_reference_configs.register(reference)

    reference = ReferenceModelConfig(name="data_manager_app.CrfFour", fields=["f1"])
    site_reference_configs.register(reference)

    reference = ReferenceModelConfig(name="data_manager_app.CrfFive", fields=["f1"])
    site_reference_configs.register(reference)

    reference = ReferenceModelConfig(name="data_manager_app.CrfSix", fields=["f1"])
    site_reference_configs.register(reference)

    reference = ReferenceModelConfig(name="data_manager_app.CrfSeven", fields=["f1"])
    site_reference_configs.register(reference)

    reference = ReferenceModelConfig(
        name="data_manager_app.CrfMissingManager", fields=["f1"]
    )
    site_reference_configs.register(reference)
