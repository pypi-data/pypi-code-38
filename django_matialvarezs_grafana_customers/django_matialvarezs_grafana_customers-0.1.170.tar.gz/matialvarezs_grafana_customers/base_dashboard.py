import json
from . import settings

def get_dashboard():
    return {
        # "__inputs": [
        #     {
        #         "name": "settings.DATASOURCE_NAME",
        #         "label": "settings.DATASOURCE_NAME",
        #         "description": "",
        #         "type": "datasource",
        #         "pluginId": "postgres",
        #         "pluginName": "PostgreSQL"
        #     }
        # ],
        # "__requires": [
        #     {
        #         "type": "grafana",
        #         "id": "grafana",
        #         "name": "Grafana",
        #         "version": "5.0.4"
        #     },
        #     {
        #         "type": "panel",
        #         "id": "graph",
        #         "name": "Graph",
        #         "version": "5.0.0"
        #     },
        #     {
        #         "type": "datasource",
        #         "id": "postgres",
        #         "name": "PostgreSQL",
        #         "version": "5.0.0"
        #     }
        # ],
        "annotations": {
            "list": [
                {
                    "builtIn": 1,
                    "datasource": "-- Grafana --",
                    "enable": True,
                    "hide": True,
                    "iconColor": "rgba(0, 211, 255, 1)",
                    "name": "Annotations & Alerts",
                    "type": "dashboard"
                }
            ]
        },
        "editable": True,
        "gnetId": None,
        "graphTooltip": 2,
        "id": None,
        "links": [],
        #"panels": [],#panels,
        "refresh": "5s",
        "schemaVersion": 16,
        "style": "dark",
        "tags": [],
        "templating": {
            "list": []
        },
        "time": {
            "from": "now-24h",
            "to": "now"
        },
        "timepicker": {
            "refresh_intervals": [
                "5s",
                "10s",
                "30s",
                "1m",
                "5m",
                "15m",
                "30m",
                "1h",
                "2h",
                "1d"
            ],
            "time_options": [
                "5m",
                "15m",
                "1h",
                "6h",
                "12h",
                "24h",
                "2d",
                "7d",
                "30d"
            ]
        },
        "timezone": "browser",
        "title": "",
        "uid": None,
        "version": 3
    }
