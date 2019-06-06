from strictyaml import Any, Map, MapPattern, Optional, Seq, Str

from libflavour.fields import FieldFactory


schema_addon = Map(
    {
        "name": Str(),
        "version": Str(),
        Optional("install"): MapPattern(Str(), Any(), minimum_keys=1),
        "flavour": Map(
            {
                "version": Str(),
                # project configuration per addon
                # flavour version per addon
                # backing services with configuration
            }
        ),
        Optional("form"): MapPattern(Str(), Any(), minimum_keys=1),
    }
)


schema_project = Map(
    {
        "slug": Str(),
        "version": Str(),
        # buildpacks
        # options for buildpacks
        "flavour": Map({"version": Str()}),
        Optional("services"): MapPattern(Str(), Map({"type": Str()})),
        Optional("addons"): MapPattern(
            Str(),
            Map(
                {
                    "manager": Str(),
                    Optional("settings"): MapPattern(Str(), Any(), minimum_keys=1),
                }
            ),
            minimum_keys=1,
        ),
        Optional("form"): MapPattern(Str(), Any(), minimum_keys=1),
    }
)
