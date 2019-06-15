default_config={
    "origin": {"folders":["prestatic/"]},
    "destination": {"folder": "templates/",
                    "exts": ["htm", "htm"],
                    "type": "embed",
                    "basefolderlink": "/static/"},
    "export": {"enabled": True,
               "rules": []},
    "anchors": {"js": {"start": "<!--MinipushJSExport-Start-->",
                       "end": "<!--MinipushJSExport-End-->"},
                "css": {"start": "<!--MinipushCSSExport-Start-->",
                        "end": "<!--MinipushCSSExport-End-->"},
                "conf": {"start": "<!--MinipushExport-Start->",
                         "end": "<-MinipushExport-End-->"}
                },
    "format":{"embed":{"js": "<!--{filename}--><script>{content}</script>",
                       "css": "<!--{filename}--><style>{content}</style>"},
              "link":{"js": "<script src='{path}'/>",
                      "css": "<link href='{path}' rel='stylesheet'/>"}
            },
    "cache": {"folder": "static/",
              "enabled": True}
}
