from edc_reference import ReferenceModelConfig, site_reference_configs


def register_to_site_reference_configs():
    site_reference_configs.registry = {}

    reference = ReferenceModelConfig(name="dashboard_app.CrfOne", fields=["f1"])
    site_reference_configs.register(reference)

    reference = ReferenceModelConfig(name="dashboard_app.CrfTwo", fields=["f1"])
    site_reference_configs.register(reference)

    reference = ReferenceModelConfig(name="dashboard_app.CrfThree", fields=["f1"])
    site_reference_configs.register(reference)

    reference = ReferenceModelConfig(name="dashboard_app.CrfFour", fields=["f1"])
    site_reference_configs.register(reference)

    reference = ReferenceModelConfig(name="dashboard_app.CrfFive", fields=["f1"])
    site_reference_configs.register(reference)

    reference = ReferenceModelConfig(name="dashboard_app.CrfSix", fields=["f1"])
    site_reference_configs.register(reference)

    reference = ReferenceModelConfig(name="dashboard_app.CrfSeven", fields=["f1"])
    site_reference_configs.register(reference)

    reference = ReferenceModelConfig(
        name="dashboard_app.CrfMissingManager", fields=["f1"]
    )
    site_reference_configs.register(reference)
