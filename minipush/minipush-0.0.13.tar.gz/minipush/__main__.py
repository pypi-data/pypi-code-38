"""
Minipush
Copyright (c) 2019 Rémi LANGDORPH
Software under MIT license
https://opensource.org/licenses/mit-license.php
"""
##version#start##
__version__='0.0.13'
##version#end##
__doc__="""
minipush v"""+__version__+""" by Rémi "Mr e-RL" LANGDORPH
(c)2019 Rémi LANGDORPH - mrerl@warlegend.net

This script supports the followings filetypes: css, js
Config: You have to create a file named 'config.json', if possible in the script folder.
{
    "origin": {"folders":["css/", "js/core/", "js/plugins/", "js/"]},
    "destination": {"folder": "../templates/", "exts": ["htm", "html"], "type": "embed", "basefolderlink": "/static/"},
    "anchors": {"js": {"start": "<!--AutomatedJSExport-Start-->",
                "end": "<!--AutomatedJSExport-End-->"},
                "css": {"start": "<!--AutomatedCSSExport-Start-->",
                        "end": "<!--AutomatedCSSExport-End-->"},
                "conf": {"start": "<!--AutomatedExport-Start->",
                        "end": "<-AutomatedExport-End-->"}
                },
    "format":{"embed":{"js": "<!--{filename}--><script>{content}</script>",
                       "css": "<!--{filename}--><style>{content}</style>"},
              "link":{"js": "<script src='{path}'/>",
                      "css": "<link href='{path}' rel='stylesheet'/>"}
            },
    "cache": {"folder": "../static/",
              "enabled": true}
}

Arguments:
command      argument         description
-c --config  {configfile}     set the config file to load
-j --json    '{configjson}'   set the config from json
-C --clear                    remove all the scripts from the templates
-h --help                     show help
-v --version                  show version
"""
from .push import *
print_status=True
def main():
    global config
    if "-v" in sys.argv or "--version" in sys.argv:
        print(__version__)
        return
    if "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__)
        return
    if "-c" in sys.argv or "--config" in sys.argv:
        for x, arg in enumerate(sys.argv):
            if (arg=="-c" or arg=="--config"):
                try:
                    config=json.load(open(sys.argv[x+1]))
                except Exception as e:
                    print(e)
                    return
    elif "-j" in sys.argv or "--json" in sys.argv:
        for x, arg in enumerate(sys.argv):
            if (arg=="-j" or arg=="--json"):
                try:
                    config=json.loads(sys.argv[x+1])
                except Exception as e:
                    print(e)
                    return
    else:
        try:
            config=json.load(open("config.json"))
        except Exception as e:
            print(e)
            return
    if "-C" in sys.argv or "--clear" in sys.argv:
        print("removing scripts & styles in templates files")
        edit_templates(config["destination"]["folder"], config["destination"]["exts"], {"js": {}, "css": {}}, config)
        return
    else:
        print(f"""Cache: {'ON' if cache_status(config) else 'OFF'} \t   Origins: {' '.join(["'"+_+"'" for _ in config['origin']['folders']])} \t  Destination: {"'"+config['destination']['folder']+"'"} ({', '.join(["'*."+_+"'" for _ in config['destination']['exts']])})""")
        scripts={"js": {}, "css": {}}
        cfiles={}
        cpath=None
        o=get_origins(config["origin"]["folders"], ["js", "css"])
        osize=len(o)
        if cache_status(config):
            cfiles=get_cached_files(config["cache"]["folder"])
            cpath=config["cache"]["folder"]
        print(f"Minimizing {len(o)} files...")
        l=[]
        n=1
        for _ in o:
            m=min(_, cfiles, cpath, f"[{n}/{osize}]\t")
            n+=1
            l.append(m)
            if m["status"]=="success":
                if m["type"]=="js":
                    scripts["js"][_]=m["result"]
                if m["type"]=="css":
                    scripts["css"][_]=m["result"]
        edit_templates(config["destination"]["folder"], config["destination"]["exts"], scripts, config)
        if export_status(config): export(scripts, config["export"]["rules"], config["format"]["export"])
        if cache_status(config): export_cache(l, config)
if __name__=="__main__":
    main()
