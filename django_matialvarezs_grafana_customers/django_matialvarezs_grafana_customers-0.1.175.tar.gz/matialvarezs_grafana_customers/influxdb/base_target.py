def get_target_panel(measurement,field,**options):
    alias = options.get("alias","")
    return {
        "alias":alias,
        "groupBy": [],
        "measurement": measurement,
        "orderByTime": "ASC",
        "policy": "default",
        "refId": "A",
        "resultFormat": "time_series",
        "select": [
            [
                {
                    "params": [
                        field
                    ],
                    "type": "field"
                }
            ]
        ],
        "tags": []
    }
