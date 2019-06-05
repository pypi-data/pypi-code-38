import delune
import json

def __mount__ (app):
    @app.route ("/<alias>/documents", methods = ["POST", "DELETE", "OPTIONS"])
    @app.permission_required ("index")
    def documents (was, alias, truncate_confirm = "", q = "", lang = "en", analyze = 1):
        if was.request.method == "DELETE":
            if q:
                delune.get (alias).queue (1, json.dumps ({"query": {'qs': q, 'lang': lang, 'analyze': analyze}}))
                return was.response.API ("202 Accepted")
            elif truncate_confirm != alias:
                return was.response.Fault ("400 Bad Request", 40003, 'parameter truncate_confirm=(alias name) required')            
            delune.get (alias).queue.truncate ()
            return was.response.API ("202 Accepted")        
        delune.get (alias).queue (0, was.request.body)
        return was.response.API ("202 Accepted")
    
    @app.route ("/<alias>/documents/<_id>", methods = ["DELETE", "PUT", "OPTIONS"])
    @app.permission_required ("index")
    def cud (was, alias, _id, nthdoc = 0):
        delune.get (alias).queue (1, json.dumps ({"query": {'qs': "_id:" + _id}}))
        if was.request.method == "PUT":
            delune.get (alias).queue (0, was.request.body)
        return was.response.API ("202 Accepted")
        
    # -------------------------------------------------------------
    
    @app.route ("/<alias>/documents/<_id>", methods = ["GET"])    
    def get (was, alias, _id, nthdoc = 0):
        return was.response.API (delune.query (alias, "_id:" + _id, nthdoc = nthdoc))
    
    @app.route ("/<alias>/documents", methods = ["GET", "PUT", "OPTIONS"])
    def query (was, alias, **args):
        q = args.get ("q")
        if not q:
            return was.response.Fault ("400 Bad Request", 40003, 'parameter q required')
        
        l = args.get ("lang", "en")
        analyze = args.get ("analyze", 1)
        
        o = args.get ("offset", 0)
        f = args.get ("limit", 10)
        s = args.get ("sort", "")
        w = args.get ("snippet", 30)    
        r = args.get ("partial", "")
        d = args.get ("nth_content", 0)    
        data = args.get ("data", 1)
        
        if type (q) is list:
            return was.response.API ([delune.query (alias, eq, o, f, s, w, r, l, d, analyze, data, limit = 1) for eq in q])
        return was.response.API (delune.query (alias, q, o, f, s, w, r, d, l, analyze, data, limit = 1))
    