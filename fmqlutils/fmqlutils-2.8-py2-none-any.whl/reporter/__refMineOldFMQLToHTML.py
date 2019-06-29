#!/usr/bin/env python

#
# A Python equivalent of the Javascript HTML utilities in fmUtils.js
#

"""
A simple class to produce HTML from JSON reply. Parallels function in
JS utility. Used for server-side HTML.

TBD QUICKS:
- Why does going to HTML mean must do utf-8 (see WSGI) for some files. ex/ 9002313_82522 (see test at bottom)
- TOPONLY in SELECT TYPES (fixed now)
- Break out URI in URI Maker interface. Then supply a Rambler etc. one when initialized. URI switching is the most complex item. This will also play well for a Patient Graph URI projection ie/ /patient/9/120_5 etc. 2-9 ref must become patient/9 etc. And 120_5 itself. patient/9/120_5-1 etc. ie. this is the first map. Note: could be doing this to JSON instead ie/ part of a JSON-centric mapping to one scheme or another. Otherwise this would need suppression/pred map support and I don't want that. Though could have some ie/ predicate normalizer.
  ... ultimately may become a builder shared with RDF etc.

BIGGER:
- waiting on FMQL. DESCRIBE X IN ... or SELECT IN ... can't walk down so get into trouble with some links.

Longer run: better into HTML5. Idea of VistA turned in a navigatable document with tags (ala blogs). Tags are the concepts so to use a concept in a resource means to tag it. This highlights how key SAMEAS is. It tags the published data and you want as many tags as possible.
- will add more tag support

REM: also need to better support the difference between markup for an application and simple pages (may split out). ie/ for Rambler, the app vs.

Note: this is not (YET) for a linked patient data view of VistA which would be patient and not file centered.
"""

import re
import StringIO
from operator import itemgetter

SAMEASBASE = "http://schemes.caregraf.info/"
LIMIT = 100
CLIMIT = 10

HTML_TEMPL = """<!doctype html>
<html>
<head>
<title>{0!s}</title>
<!--[if IE]>
<meta http-equiv="X-UA-Compatible" content="IE=Edge,chrome=1"/>
<![endif]-->
<meta charset="utf-8"/>
<meta name="application-name" content="FileMan Schema"/>
<meta name="fragment" content="!">
<link rel='stylesheet' href='fmBase.css' type='text/css'>
</head>
<body>
<div id="header">
<h1 id="logo"><a href="index.html">{1!s}</a></h1>
</div>
<div id="fmql">
{2!s}
</div>
<div id="footer"><a href="http://www.caregraf.info">Master FileMan's Data</a>&trade; (c) 2017 <span id="flogo"><a href="http://www.caregraf.info">Caregraf</a></span></div>
</body>
</html>
"""

class OldJSONToHTML:
    """
    Returns a div of class 'results' or 'error' with JSON rendered as HTML
    """
    def __init__(self, urlForm="FILE", dataBase="/rambler#!", schemaBase="/schema#!"):
        self.urlForm = urlForm
        self.mu = StringIO.StringIO()
        # Only needed if urlForm != FILE
        self.dataBase = dataBase
        self.schemaBase = schemaBase 
        
    def processReply(self, jReply):
        """
        Ala JtoR: common form of entries.
        
        Note: this is NOT designed for reply after reply inlined. It does support next-next.
        """
        if "error" in jReply:
            self.mu.write("<div class='error'><p>Error: %s</p></div>" % jReply["error"])
            return
        if "fmql" not in jReply:
            self.mu.write("<div class='error'><p>Unsupported Reply Format</p></div>")
            return
        queryType = jReply["fmql"]["OP"]
        if queryType == "SELECT":
            self.processSelect(jReply)
        elif queryType == "DESCRIBE":
            self.processDescribe(jReply)
        elif queryType == "COUNT REFS":
            self.processCountRefs(jReply)
        elif queryType == "COUNT":
            self.processCount(jReply)
        elif queryType == "SELECT TYPES":
            self.processSelectAllTypes(jReply)
        elif queryType == "DESCRIBE TYPE":
            self.processDescribeType(jReply)
        # starts as SELECTALLREFERRERSTOTYPE
        elif queryType == "SELECT TYPE REFS":
            self.processSelectTypeRefs(jReply)
        else:
            raise Exception("QPERROR", "Unsupported Query Type %s" % queryType) # should never get here
        
    def processReplyToTitle(self, jReply, prefix=""):
        """
        HTML only: some want full page with title. For now, easy is to give the arguments in the Reply.
        
        Ex of prefix: apps
        """
        title = prefix + ": " 
        title += jReply["fmql"]["OP"]
        if "TYPELABEL" in jReply["fmql"]:
            title += " " + jReply["fmql"]["TYPELABEL"] + " (" + jReply["fmql"]["TYPE"] + ")"
        elif "URI" in jReply["fmql"]:
            title += " " + jReply["fmql"]["URI"]
        return title
        
    def processReplyToTags(self, jReply):
        """
        rel=tag ala blogs
        - same as k3
        - will tie in datasets.cg.org/vs ... ie/ as a tag for appropriate pages ie/ tag support as an option.
        """
        pass
            
    def done(self):
        self.mu.seek(0,0)
        return self.mu 
        
    # ################ Node Data #######################
    
    def processSelect(self, jReply):
        """
        SELECT is really a navigation item ie/ <nav> ... It's a starting off point. May allow nav rather than table styling. Need more HTML5 knowhow.
        """
        results = jReply["results"]        
        if len(results) == 0:
            self.mu.write("<p>No entries</p>")
            return
        self.mu.write("<h3>%s</h3>" % jReply["fmql"]["TYPELABEL"])
        self.mu.write("<table class='selectResults'>")    
        offset = int(jReply["fmql"]["OFFSET"])
        i = 0;
        for result in results:
            # TBD: should never get "empty" dictionaries
            if "uri" not in result:
                i += 1
                continue        
            label = result["uri"]["label"].split("/")[1] 
            resultsMarkup = "<tr><td>" + str(offset + i + 1) + ".</td><td><a href=\""  
            link = self.__makeLink(self.dataBase, result["uri"]["value"], op="DESCRIBE") 
            resultsMarkup += link + "\">" + label + "</a></td>"        
            if "sameAs" in result["uri"]:
                resultsMarkup += "<td>" + self.__sameAsLink(result["uri"]) + "</td>"        
                resultsMarkup += "</tr>"        
            i += 1
            self.mu.write(resultsMarkup)
        self.mu.write("</table>")      
        # pager must go in with result
        navMarkup = self.__makeNavMarkup(jReply)        
        if navMarkup:
            self.mu.write(navMarkup)        

    def processDescribe(self, jReply):
        if len(jReply["results"]) == 0:
            self.mu.write("<p>No entries</p>")
            return
        fileId = jReply["results"][0]["uri"]["value"].split("-")[0]
        fileURI = self.__makeLink(self.dataBase, fileId, "SELECT", limit="100")
        for i in range(0, len(jReply["results"])):
            result = jReply["results"][i]
            fileLabel = re.search(r'([^\/]+)\/[^\/]+$', result["uri"]["label"]).group(1)
            numberMU = str(i+1) + ". " if len(jReply["results"]) > 1 else ""
            header = "<h3>" + numberMU + "<a href='" + fileURI + "'>" + fileLabel + "</a> > " + result["uri"]["label"].split("/")[1] + " (" + result["uri"]["value"].split("-")[1] + ")"
            if "sameAs" in result["uri"]:
                header += " (%s)" % self.__sameAsLink(result["uri"])
            header += "</h3>"
            self.mu.write(header)
            self.mu.write(self.__descriptionFieldsAsDL(result))
            if len(jReply["results"]) > 1 and i != (len(jReply["results"]) - 1):
                self.mu.write("<hr/>")
        navMarkup = self.__makeNavMarkup(jReply)
        if navMarkup:
            self.mu.write(navMarkup)        
        
    def __descriptionFieldsAsDL(self, result, resultsMarkup=""):
        resultsMarkup += "<dl>"
        fields = []
        for field in result:
            if field == "uri": 
                continue
            id = result[field]["fmId"]
            fields.append((id, field))
        fields.sort(key=itemgetter(0))
        for fieldInfo in fields:
            field = fieldInfo[1]
            displayField = re.sub(r'_$', "", re.sub(r'_', ' ' , field))
            if result[field]["type"] == "uri":
                sameAsMU = ""
                if "sameAs" in result[field]:
                    sameAsMU = " (%s)" %  self.__sameAsLink(result[field])
                ahref = self.__makeLink(self.dataBase, result[field]["value"], "DESCRIBE")
                resultsMarkup += "<dt>" + displayField + "</dt><dd><a href=\"" + ahref + "\">" + result[field]["label"] + "</a>" + sameAsMU + "</dd>"                
            elif result[field]["type"] == "typed-literal": 
                if re.search(r'XMLLiteral$', result[field]["datatype"]):
                    resultsMarkup += "<dt>" + displayField + "</dt><dd><pre>" + result[field]["value"] + "</pre></dd>"            
                else: # Date: 22-rdf-syntax-ns#dateTime
                    resultsMarkup += "<dt>" + displayField + "</dt><dd>" + result[field]["value"] + "</dd>"
            elif result[field]["type"] == "cnodes":
                resultsMarkup += "<dt>" + displayField + "</dt><dd>"
                if "stopped" in result[field]:
                    resultsMarkup += "Too many to show: count > CSTOP."
                    cNodeQuery = "DESCRIBE " + result[field]["file"] + " IN " + result["uri"]["value"] + " LIMIT " + str(CLIMIT)
                    # TBD: cnode in cnode should NOT get this
                    resultsMarkup += " <a href='/query?fmql=" + cNodeQuery + "&format=HTML'>View in Query Maker</a>"  
                else:
                    resultsMarkup += "<ol class='multiple'>"
                    for bresult in result[field]["value"]:
                        labelSearch = re.search(r'([^\/]+)\/[^\/]+$', bresult["uri"]["label"])
                        sfileLabel = labelSearch.group(1) if labelSearch else bresult["uri"]["label"] # synth 99999999 is different
                        resultsMarkup += "<li><h3>" + sfileLabel + ":" + bresult["uri"]["value"] + "</h3>"
                        resultsMarkup = self.__descriptionFieldsAsDL(bresult, resultsMarkup)
                        resultsMarkup += "</li>"
                    resultsMarkup += "</ol>"
                resultsMarkup += "</dd>"
            else:
                resultsMarkup += "<dt>" + displayField + "</dt><dd>" + result[field]["value"] + "</dd>"
        resultsMarkup += "</dl>"
        return resultsMarkup
        
    def processCountRefs(self, jReply):
        if len(jReply["results"]) == 0:
            self.mu.write("<p>No entries</p>")
            return
        self.mu.write("<h3>References to %s</h3>" % jReply["fmql"]["URI"])
        self.mu.write("<table>")
        for i in range(0, len(jReply["results"])):
            result = jReply["results"][i]
            resultsMarkup = "<tr>"
            resultsMarkup += "<td>" + result["fileLabel"] + " (" + result["file"] + ")" + "</td>"
            resultsMarkup += "<td>" + result["fieldLabel"] + " (" + result["field"] + ")" + "</td>"
            resultsMarkup += "<td><a href='"
            filter = result["field"] + "=" + jReply["fmql"]["URI"]            
            rurl = self.__makeLink(self.dataBase, result["file"], "SELECT", filter, str(LIMIT))
            resultsMarkup += rurl
            resultsMarkup += "'>" + result["count"] + "</a>" + "</td>"
            resultsMarkup += "</tr>"
            self.mu.write(resultsMarkup)
        self.mu.write("</table>")
        
    def processCount(self, jReply):
        self.mu.write("<p>" + jReply["count"] + "</p>")

    def __sameAsLink(self, uriValue):
        """
        Per HTML5, making rel=tag here. This is usually used for tagging in blogs but in effect canonical concepts tag pages. That the layout puts these "tags" beside the link they match doesn't highlight this well enough.
        """
        sameasURI = uriValue["sameAs"];
        if sameasURI == "LOCAL":
            return "LOCAL"
        lMatch = re.match(r'LOCAL:([\d\-]+)$', sameasURI)
        if lMatch:
            return "<a href='" + self.dataBase + lMatch.group(1) + "'  rel='tag'>" + sameasURI + "</a>";
        # TBD: HL7, ICD, CPT etc.
        sameas = sameasURI.replace(".", "_").replace("VA:", SAMEASBASE + "va/").replace("ICD9:", SAMEASBASE + "icd9/").replace("CPT:", SAMEASBASE + "cpt/").replace("PROVIDER:", SAMEASBASE + "provider/");
        return "<a href='" + sameas + "' rel='tag'>" + sameasURI + "</a>";

    def __makeNavMarkup(self, reply):
        """
        Uses HTML5 next, prev rel tags (note: no up or start any more: this is the only official navigation tagging)
        """
        navMarkup = ""    
    
        args = reply["fmql"]    

        if "OFFSET" not in args:
            return navMarkup    

        if args["OFFSET"] != "0":
            offset = int(args["OFFSET"])    
            navMarkup = "<div class='pager'>"    
            prevURI = ""    
            poffset = offset - int(args["LIMIT"]) 
            prevURI = self.__makeLink(self.dataBase, args["TYPE"], op=args["OP"], filter=args["FILTER"] if "FILTER" in args else "", limit=args["LIMIT"], offset = str(poffset) if poffset > 0 else "")
            navMarkup += "<a href='" + prevURI + "' rel='prev'>PREV</a>"  
        else:
            offset = 0    
            
        # Going to need a next
        if args["LIMIT"] == str(len(reply["results"])): 
            if navMarkup == "":
                navMarkup = "<div class='pager'>"    
            else:
                navMarkup += " | "    
            nextURI = ""    
            noffset = int(args["LIMIT"]) + offset 
            nextURI = self.__makeLink(self.dataBase, args["TYPE"], op=args["OP"], filter=args["FILTER"] if "FILTER" in args else "", limit=args["LIMIT"], offset=str(noffset))
            navMarkup += "<a href='" + nextURI + "' rel='next'>NEXT</a>"    
            
        if navMarkup:
            navMarkup += " (" + args["LIMIT"] + ")"
            navMarkup += "</div>"    
            
        return navMarkup
                
    # ################### Schema ##################
    
    def processSelectAllTypes(self, jsn):
        """
        There is an argument to turn this into HTML nav tags ie/ if VistA is being presented as a site of documents, then here is the table of contents/the outline.
        
        Note: in time, PICS should come into play providing a higher level categorization.
        """
        results = jsn["results"]
        tresults = [result for result in results if "parent" not in result]
        totalRecords = sum(int(result["count"]) for result in tresults if "count" in result)
        
        self.mu.write("<div><h1>Files: {:,} - Records: {:,}</h1></div>".format(len(tresults), totalRecords))
                
        countResultsOrdered = sorted(tresults, key=lambda x: float(x["count"] if "count" in x else 0), reverse=True)
        # Top Twenty Five
        topTwentyFiveMU = """
        <div>
        <div><h3>Top 25 Files</h3></div>
        <table>
        <tr><th>#</th><th>Id</th><th>Name</th><th>Count</th></tr>
        """
        for i, result in enumerate(countResultsOrdered, 1):
            svalue = re.sub(r'\.', '_', result["number"])
            linkName = "<a href=\"%s\">%s</a></td>" % (self.__makeLink(self.schemaBase, svalue), result["name"])            
            trMU = "<tr><td>{}</td><td>{}</td><td>{}</td><td>{:,}</td></tr>".format(i, result["number"], linkName, int(result["count"]))
            topTwentyFiveMU += trMU
            if i == 25:
                break
        topTwentyFiveMU += "</table></div>"
        self.mu.write(topTwentyFiveMU)
        
        self.mu.write("<div id=\"results\"><h3>All Top Files</h3>")
        self.mu.write("<table><thead><tr>")
        fields = ["Id", "name", "global", "count"]
        for field in fields:
            self.mu.write("<th>" + field.capitalize() + "</th>")
        self.mu.write("</tr></thead><tbody>")
        for result in tresults:
            value = result["number"]
            resultsMarkup = "<tr><td>%s</td>" % (value)
            svalue = re.sub(r'\.', '_', value)
            link = self.__makeLink(self.schemaBase, svalue)
            resultsMarkup += "<td id=\"%s\"><a href=\"%s\">%s</a></td>" % (value, link, result["name"])
            resultsMarkup += "<td>%s</td>" % result["global"]
            if "count" in result:
                try:
                    resultsMarkup += "<td>{:,}</td>".format(int(result["count"]))
                except:
                    resultsMarkup += "<td>" + result["count"] + "</td>"
            else:
                resultsMarkup += "<td/>"
            resultsMarkup += "</tr>"
            self.mu.write(resultsMarkup)
        self.mu.write("</tbody></table>")  
        self.mu.write("</div>")
                
    def processDescribeType(self, jsn):
        """
        Returns:
            <div id=resultsHeader>...Header</div>
            <div id=results>...results</div>
        ... can be combined inside a <div class="fmqlResults" along with
        SELECT TYPE REFs response.
        """
        
        link = self.__makeLink(self.schemaBase, "", "SELECT TYPES TOPONLY")
        self.mu.write("<div id=\"resultsHeader\"><h1><a href='%s'>Files</a> > %s</h1></div>" % (link, jsn["fmql"]["TYPELABEL"]))
        
        self.mu.write("<div id=\"results\">")
        
        fileId = jsn["number"]
        resultsMarkup = "<dl>"
        keys = ["parent", "name", "number", "location", "description", "applicationGroups"]
        for key in keys:
            if key not in jsn:
                continue
            if key == "fields":
                continue
            if key == "description":
                value = jsn[key]["value"]
            elif key == "parent":
                link = self.__makeLink(self.schemaBase, re.sub("\.", "_", jsn["parent"]), op="DESCRIBE TYPE")
                value = "<a href=\"" + link + "\">" + jsn["parent"] + "</a>"
            else:
                value = jsn[key]
            resultsMarkup += "<dt>" + key + "</dt><dd>" + value + "</dd>"

        resultsMarkup += "<dt>Fields</dt><dd>"
        fields = ["number", "name", "location", "type", "details", "index", "description"]
        fieldNames = ["#", "Name", "Location", "Type", "Details", "Index", "Description"]
                
        results = jsn["fields"]
        resultsMarkup += "<table><thead><tr>"
        for fieldName in fieldNames:    
            resultsMarkup += "<th>" + fieldName + "</th>"
        resultsMarkup += "</tr></thead><tbody>"
        
        self.mu.write(resultsMarkup)
        
        for result in results:
            trMarkup = "<tr>"
            for field in fields:
                if field in result:
                    value = result[field]
                    # account for required and add + to name
                    if field == "name":
                        value = re.sub(r'\_', ' ', value).lower()
                        trMarkup += "<td>" + value
                        if re.search(r'R', result["flags"]):
                            trMarkup += "(+)</td>"
                        else:
                            trMarkup += "</td>"
                    elif field == "type":
                        trMarkup += "<td>" + self.__typeIdToLabel(value) + "</td>"
                    elif field == "details":
                        values = result["details"]
                        if result["type"] == "7" or result["type"] == "9":
                            link = self.__makeLink(self.schemaBase, re.sub("\.", "_", values), op="DESCRIBE TYPE")
                            trMarkup += "<td><a href=\"" + link + "\">" + values + "</a></td>"
                        elif result["type"] == "3" or result["type"] == "12":
                            values = values.split(";")
                            trMarkup += "<td>"
                            cvmu = ""
                            for codeValue in values:
                                if cvmu != "":
                                    cvmu += "<br/>" + codeValue
                                else: 
                                    cvmu = codeValue
                            trMarkup += cvmu + "</td>"
                        elif result["type"] == "8":
                            values = values.split(";")
                            trMarkup += "<td>"
                            vpmu = ""
                            for vpval in values:
                                link = self.__makeLink(self.schemaBase, re.sub("\.", "_", vpval), op="DESCRIBE TYPE")
                                alnk = "<a href=\"" + link + "\">" + vpval + "</a>"
                                if vpmu != "":
                                    vpmu += ", " + alnk
                                else:
                                    vpmu = alnk
                            trMarkup += vpmu + "</td>"
                        # CHCS SPECIAL: see dna_flag is 2 which is of type 12? and has YES:NO details ala an enum but ignored
                        else:
                            trMarkup += "<td></td>"
                    elif field == "description":
                        trMarkup += "<td>" + value["value"] + "</td>"  
                    else:
                        trMarkup += "<td>" + value + "</td>"
                else:
                    trMarkup += "<td></td>"
            trMarkup += "</tr>"
            self.mu.write(trMarkup)
        self.mu.write("</tbody></table></dd></dl>")
        self.mu.write("</div>") # id=results
                
    # CHCS SPECIAL: 12 (in PATIENT 2) not recognized
    def __typeIdToLabel(self, typeId):
        FIELDTYPES = {
            "1": "DATE-TIME",
            "2": "NUMERIC",
            "3": "SET OF CODES",
            "4": "FREE TEXT",
            "5": "WORD-PROCESSING",
            "6": "COMPUTED",
            "7": "POINTER",
            "8": "VARIABLE-POINTER",
            "9": "MULTIPLE",
            "10": "MUMPS",
           
            "12": "BOOLEAN"
        }  
        if typeId not in FIELDTYPES:
            return typeId
        return FIELDTYPES[typeId]
        
    def processSelectTypeRefs(self, reply):
        """
        TBD: may expose file id as well as referring predicates)
        """
        if len(reply["results"]) == 0:
            self.mu.write("<p>Not Referenced</p>")
            return
        self.mu.write("<h2>Referenced by %d types</h2>" % len(reply["results"]))
        self.mu.write("<ol>")
        for i in range(0, len(reply["results"])):
            result = reply["results"][i]
            rurl = self.__makeLink(self.schemaBase, re.sub(r'\.', '_', result["rfile"]), op="DESCRIBE TYPE")
            rfieldLabels = ""
            for k in range(0, len(result["rfields"])):
                if rfieldLabels:
                    rfieldLabels += ", "
                rfieldLabels += result["rfields"][k]["rfieldLabel"].lower()
            self.mu.write("<li><a href=\"" + rurl + "\">" + result["rfileLabel"] + "</a> (" + result["rfile"] + ")" + " -- " + rfieldLabels + "</li>")
        self.mu.write("</ol>")
        
    # ############ Common Utilities ###########
        
    def __makeLink(self, base, uri, op="SELECT", filter="", limit="", offset=""):

        base = "/" if not base else base
        if self.urlForm == "URI":
            link = base + uri
            qualifiers = ""
            if filter:
                qualifiers = "/%s/%s/%s" % (limit if limit else "100", offset if offset else "0", filter)
            elif limit:
                qualifiers = "/" + limit
                if offset:
                    qualifiers += "/" + offset
            link += qualifiers  
        elif self.urlForm == "QUERY":
            query = op + " " + uri
            if filter:
                query +=  " FILTER(" + filter + ")"
            if limit:
                query += " LIMIT " + limit
                if offset:
                    query += " OFFSET " + offset
            link = "/query?fmql=" + query + "&format=HTML"
        else: # "FILE"
            if not uri:
                uri = "index"
            link = uri + ".html"    
        
        return link

# ############################ Generate Schema HTML ##############################

def generateSchemaHTML(systemTitle, schemaReplyLocn, outputHTMLLocn):

    """
    Reads Schema and produces a HTML "site"

    TODO: CHCS SPECIAL: see dna_flag is 2 which is of type 12? and has YES:NO details ala an enum but ignored
    """
    for fl in os.listdir(schemaReplyLocn):
        if fl == "SELECT_TYPES.json":
            outputFile = "index"
        elif re.match(r'(DESCRIBE TYPE |SCHEMA\_)', fl):
            flId = re.match(r'(DESCRIBE TYPE |SCHEMA\_)([^\.]+)\.json$', fl).group(2)
            outputFile = flId
        else:
            continue

        # Schema
        toHTML = OldJSONToHTML(urlForm="FILE")
        schemaReply = json.load(open(schemaReplyLocn + fl))
        toHTML.processReply(schemaReply)
        mu = toHTML.done().getvalue()

        # let's load the REF
        try:
            refFL = "REFS_{}.json".format(flId)
            refReply = json.load(open(schemaReplyLocn + refFL))
            toHTML = OldJSONToHTML(urlForm="FILE")
            toHTML.processReply(refReply)
            rmu = toHTML.done().getvalue()
        except:
            rmu = "<p>No REFERENCES reply available to process</p>"

        fmqlResultsWrap = """<div class=\"fmqlResults\">{}</div>"""
        wrappedMU = fmqlResultsWrap.format(mu.encode("utf-8"))
        wrappedRMU = fmqlResultsWrap.format(rmu.encode("utf-8"))
        allMU = wrappedMU + "<hr>" + wrappedRMU
        html = HTML_TEMPL.format(systemTitle, systemTitle + " Schema Browser", allMU)
        open(outputHTMLLocn + outputFile + ".html", "w").write(html)

# ############################# (Test) Driver ####################################

import os
import json

LOCN_BASE = "/data/"

def main():

    generateSchemaHTML("Cheyenne", LOCN_BASE + "cheyenne2011/JSON/", "cheyenneVISTASchemaHTML/")
    # generateSchemaHTML("nodeVISTA (FOIA)", LOCN_BASE + "nodeVISTA/JSON/", "nodeVISTASchemaHTML/")

if __name__ == "__main__":
    main()

