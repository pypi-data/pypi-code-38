from django.core.checks import Warning

from .site_reference import site_reference_configs


def check_site_reference_configs(app_configs, **kwargs):
    errors = []
    site_results = site_reference_configs.check()
    for result in site_results.values():
        errors.append(Warning(result, id=f"edc_reference.001"))
    return errors
