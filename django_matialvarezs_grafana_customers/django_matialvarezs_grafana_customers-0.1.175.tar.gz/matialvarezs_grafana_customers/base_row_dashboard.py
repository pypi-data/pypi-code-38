def get_base_row(title,id_row,**options):
    # return {
    #     "collapse": False,
    #     "height": 343,
    #     "panels": [],
    #     "repeat": None,
    #     "repeatIteration": None,
    #     "repeatRowId": None,
    #     "showTitle": True,
    #     "title": title,
    #     "titleSize": "h6"
    # }

    collapsed = options.get("collapsed",True)
    return {
               "collapsed": collapsed,
               "gridPos": {
                   "h": 1,
                   "w": 24,
                   "x": 0,
                   "y": 1
               },
               "id": id_row,
               #"panels": [],
               "title": title,
               "type": "row"
           }
