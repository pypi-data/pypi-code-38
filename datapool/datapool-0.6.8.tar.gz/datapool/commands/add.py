from ..errors import Message
from ..templates import scripts


def add(lz_folder, what, settings, print_ok, print_err, input_=input, scripts=scripts):

    if what not in scripts:
        print_err("- argument '{}' invalid. allowed values are:".format(what))
        for available_what in sorted(scripts):
            print_err("  - {}".format(available_what))
        return 1

    script = scripts[what]

    presets = _setup_presets(what, script, settings, print_err)

    if presets is None:
        return 1

    try:
        message = script.main(lz_folder, presets, input_)
        print_ok(message)
    except Message as e:
        print_err(e.message)


def _setup_presets(what, script, settings, print_err):
    available_variables = script.variables()

    presets = {}
    ok = True
    invalid_variable = False
    for setting in settings:
        if setting.count("=") != 1:
            print_err(
                "- setting '{}' invalid, required syntax is VARIABLE=VALUE".format(
                    setting
                )
            )
            ok = False
        else:
            variable, __, value = setting.partition("=")
            if variable not in available_variables:
                print_err("- variable '{}' not allowed for {}".format(variable, what))
                invalid_variable = True
                ok = False
            else:
                presets[variable] = value.strip('"').strip("'")

    if invalid_variable:
        print_err("- allowed variables are:")
        for variable in available_variables:
            print_err("  - {}".format(variable))

    if not ok:
        return None
    else:
        return presets
