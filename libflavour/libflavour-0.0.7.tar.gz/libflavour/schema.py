from strictyaml import Any, Map, MapPattern, Optional, Seq, Str

from libflavour.fields import FieldFactory


schema_addon = Map(
    {
        "version": Str(),
        Optional("install"): MapPattern(Str(), Any(), minimum_keys=1),
        "meta": Map({"name": Str(), "version": Str()}),
        Optional("config"): MapPattern(Str(), Any(), minimum_keys=1),
    }
)


schema_project = Map(
    {
        "version": Str(),
        "meta": Map({"name": Str(), "version": Str()}),
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
        Optional("config"): MapPattern(Str(), Any(), minimum_keys=1),
    }
)
