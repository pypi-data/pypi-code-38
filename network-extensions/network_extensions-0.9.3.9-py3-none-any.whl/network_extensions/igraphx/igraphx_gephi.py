""" Methoden die den Gephi-Streaming-Möglichkeiten erweitern"""

# color all edges:
import time
import progressbar
import logging
from urllib.error import URLError
logger = logging.getLogger(__name__)
from igraph.remote.gephi import GephiConnection,GephiGraphStreamer,GephiGraphStreamingAPIFormat
class GephiStreamerExtension():
    def __init__(self,stream,ctn,gr_all,ident_attr):
        """:param  GephiStreamer stream:
           :param  GephiConnection ctn:
           :param  Graph gr_all:
           :param  str ident_attr: Name des Vertex-Attributes, das eine eindeutige Zuordnung ermöglicht
           
        """
        self.stream = stream
        self.ctn = ctn
        self.gr_all = gr_all
        self.ident_attr = ident_attr
      
        self.persins = list(gr_all.vs[ident_attr])
        self.api = GephiGraphStreamingAPIFormat()
        
    def showAll(self,layout=None):
        """
        Schicke den gesamten Graphen an Gephi
        :param Layout (optional) layout: Gephi layout default fruchterman_reingold
        """
        if layout is None:
            l = self.gr_all.layout_fruchterman_reingold()
        else:
            l = layout
        self.gr_all.vs["X"]=[x[0]*10 for x in l.coords]
        self.gr_all.vs["Y"]=[x[1]*10 for x in l.coords]
        #gr_all.vs["Id"]=list(range(0,len(gr_all.vs)))
        #gr_all.vs["id"]=list(range(0,len(gr_all.vs)))
        self.stream.post(self.gr_all,self.ctn)
    
    def deleteAll(self):
        """loesche alle Knoten"""
        
        for v in self.gr_all.vs:
            v_id = "igraph:%s:v:%s"%(hex(id(self.gr_all)),v.index)
            ev = self.api.get_delete_node_event(v_id)
            self.stream.send_event(ev,self.ctn)
       
    def setForAllNode(self,vals={"label":""}):
        """setze Attribute für alle Knoten
        :param dict vals: Dictionary, dass an die Knoten übergeben wird. 
        """
        
        for v in self.gr_all.vs: #loeschen
            v_id = "igraph:%s:v:%s"%(hex(id(self.gr_all)),v.index)
            ev = self.api.get_change_node_event(v_id,vals)
            self.stream.send_event(ev,self.ctn)
            
    def setForAllEdges(self,vals={"r":0.8,"g":0.8,"b":0.8}):
        """setze Attribute für alle Kanten
        :param dict vals: Dictionary, dass an die Kanten übergeben wird. 
        """
        
        en_all={}
        for e in self.gr_all.es:
    
                s=self.gr_all.vs[e.source][self.ident_attr]
                t=self.gr_all.vs[e.target][self.ident_attr]
                
                s_id=self.persins.index(s)
                t_id=self.persins.index(t)
    
                e_id="igraph:%s:e:%s:%s"%(hex(id(self.gr_all)),s_id,t_id)
    
                en_all[e_id]= vals
    
        self.stream.send_event({"ce":en_all},self.ctn)
        
    def streamNodes(self,graphs,
                    nodes_attr,displayattr,intervall=1,sleep_time=1,
                    stream=True,year_cn=None,
                    messages_urn=None):
        """streamed die zeitliche Entwicklung von Knoten
        :param dict(graph) graphs: dict mit den zeitlichen Graphen
        :param dict nodes_attr : Ein dict mit dem Index über die Jahre.
        Dieses muss mindestens alle Jahre der Graphen enthalten.
        Für jedes Jahr liegt dort eine Liste mit:
        
        ( (wert von self.ident_attr, weitere attribute der node),value)
        Diese Struktur entspricht dem Ergebniss von :see igraphx.calcTopsForYears:
        :param bool stream: wenn False dann wird nicht gestreamed sondern nur die Events 
        für den Streamer berechnet.
        :param messages_urn: NOT USED
        :returns: streamer events
        """
        ev=self.api.get_add_node_event("YEAR")
        self.stream.send_event(ev,self.ctn)

        ev = self.api.get_change_node_event("YEAR",{"label":"year",
                                       "size":400,
                                       "r":0,"g":1,"b":0
                                      })
        self.stream.send_event(ev,self.ctn)
        
        if year_cn is not None:
            for year in graphs.keys():
                if stream:                               
                    self.stream.send_event(year_cn[year],self.ctn)
        else:
            year_cn={}
            gr_all_ls = list(self.gr_all.vs)
            for year,gr in graphs.items():
                if year%intervall !=0:
                    continue
                cn={}
                time.sleep(1)
               
                #stream.post(gr,cnt)
                bw=nodes_attr.get(year,nodes_attr.get(str(year)))
                vals={}
                for b in bw:
                    vals[b[0][0]]=(b[0][1],b[1])
                for v in gr_all_ls:
                    
                    gr_id = self.persins.index(v[displayattr])
                
                    v_id = "igraph:%s:v:%s"%(hex(id(self.gr_all)),gr_id)
                    
                    id_att = v[displayattr]
                    if id_att in vals.keys(): #gibt es den Namen unter den Top 10  
                        cn[v_id]={"size":100+min(100,vals[id_att][1]/20),
                                                             "r":1,"g":0,"b":0,
                                                             "label":id_att
                                                            }      
                    else:
                        cn[v_id]= {"label":"","size":1,"r":1,"g":1,"b":1}
                        
                #stream.post(gr_tmp,cnt)
                cn["YEAR"]={"label":year, "size":400, "r":0,"g":1,"b":0}
                         
                if stream:                               
                    self.stream.send_event({"cn":cn},self.ctn)
                year_cn[year]=cn
            
        return year_cn
    
    def streamEdges(self,
                    graphs,
                    nodes_attr,
                    displayattr,
                    intervall=1,
                    sleep_time=1,
                    stream=True,
                    year_cn=None,
                    year_en=None,
                    messages_urn=None):
    
        """streamed die zeitliche Entwicklung von Knoten und Kanten
        :param dict(graph) graphs: dict mit den zeitlichen Graphen
        :param dict nodes_attr : Ein dict mit dem Index über die Jahre.
        Dieses muss mindestens alle Jahre der Graphen enthalten.
        Für jedes Jahr liegt dort eine Liste mit:
        
        ( (wert von self.ident_attr, weitere attribute der node),value)
        Diese Struktur entspricht dem Ergebniss von :see igraphx.calcTopsForYears:
        :param bool stream: wenn False dann wird nicht gestreamed sondern nur die Events 
        für den Streamer berechnet.
        :param (optional) year_cn: Rückgabewert von stremNodes wird dann nicht neu berechnet.
        :param (optional) year_en: Rückgabewert von stremEdges wird dann nicht neu berechnet.
        :param messages_urn: NOT USED
        :returns: streamer events pro yeary
        """
        
        if year_cn is None and year_en is None:
            logger.info("no cns")
            year_cn=self.streamNodes(graphs, nodes_attr, displayattr,intervall, sleep_time, False)
            logger.info("--created")
         
        if year_en is not None:
            for year in graphs.keys():
                    if stream:
                       self.stream.send_event(year_en[year],self.ctn)
        
        else:           
            year_en={}
            for year,gr in graphs.items():
                if year%intervall !=0:
                    continue
                    
                self.setForAllEdges() # alle Kanten auf Grau
                time.sleep(0.5)
                cn=year_cn[year]
                en={}
                for e in gr.es:
                    
                    s=gr.vs[e.source][displayattr]
                    t=gr.vs[e.target][displayattr]
                    
                    
                    s_id=self.persins.index(s)
                    t_id=self.persins.index(t)
                    
                    e_id="igraph:%s:e:%s:%s"%(hex(id(self.gr_all)),s_id,t_id)
                    
                    
                    en[e_id]= {"r":1,"g":0,"b":0}
                        
             
                cn["YEAR"]={"label":year, "size":400, "r":0,"g":1,"b":0}
                
                if stream:
                    self.stream.send_event({"cn":cn,"ce":en},self.ctn)
                
                year_en[year]={"cn":cn,"ce":en}
                
        return year_en
            
settings = {"pers_pers_by_membership": {
            "description":"Personen in einer Kommission",
            "doi":"doi:10.5072/FK2/2SVCY5",
            "graph_file":"allpersons_dated_blocks.ygz",
            "file_pattern":".*blocks_(.*).graphml",
            "ident_attr":"name",
            "doi_all":"doi:10.5072/FK2/GPFUWZ",
            "graph_all_file":"allpersons_dated_blocks.graphml"
            },
        "pers_pers_by_deals_with": {
            "description":"Personen verbunden mit Personen über die verhandelt wird.",
            "doi":"doi:10.5072/FK2/2SVCY5",
            "graph_file":"kompers_directed_YEARS.ygz",
            "file_pattern":"kom_pers_directed_(.*).graphml",
            "ident_attr":"label",
            "doi_all":"doi:10.5072/FK2/GPFUWZ",
            "graph_all_file":"kom_pers_directed.graphml"
            },  
        "pers_pers_by_deals_with_and_members": {
            "description":"Personen verbunden mit Personen über die verhandelt wird und Mitglieder",
            "doi":"doi:10.5072/FK2/2SVCY5",
            "graph_file":"all_persons_members_and_deals.ygz",
            "file_pattern":".*blocks_(.*).graphml",
            "ident_attr":"label",
            "doi_all":"doi:10.5072/FK2/GPFUWZ",
            "graph_all_file":"all_persons_members_and_deals_blocks.graphml"
            
            }  
        }




if __name__ == "__main__":
    import igraph
    from igraph import igraphx

    from network_extensions import igraphx
    from dataverseTools import handleDataverse
    
    
    dv = handleDataverse.DataverseHandler("datastore-dev.mpiwg-berlin.mpg.de",
                                          "c4cacadd-d3ac-45f0-94b9-98d5396e302b",
                                         "gmpg-astronomy-gremien")
    current_setting = settings["pers_pers_by_membership"]
    content = dv.getContent(current_setting["doi_all"],current_setting["graph_all_file"])
    with open("tmp.graphml","wb") as outf:
        outf.write(content.read())
    gr_all = igraph.load(open("tmp.graphml","rb"))
    
    dv_gephi_url="http://localhost:8080/workspace1"
    ctn = GephiConnection(url=dv_gephi_url)
    stream = GephiGraphStreamer()
    
    gse = GephiStreamerExtension(stream,ctn,gr_all,current_setting["ident_attr"])
    print("load graphs")
    content = dv.getContent(current_setting["doi"],current_setting["graph_file"])
    
    graphs = igraphx.getGraphsFromFile(content,current_setting["file_pattern"])
    try:
        gse.showAll()
        gse.setForAllNode({"label":""})
        print("calc tops")
        pb = progressbar.ProgressBar()
        pb.start()
        #graphs = {k:v for k,v in graphs.items() if k < 1955}
        betw_years = igraphx.calcTopsForYears(graphs,
                                              max_len=10,
                                              displayAttr=current_setting["ident_attr"],
                                              progressBar=pb,
                                              displayAttr2="id",
                                              func="betweenness")
        print("start streaming")
        
        v = gse.streamNodes(graphs, betw_years,displayAttr)
        #v = gse.streamEdges(graphs, betw_years,current_setting["ident_attr"])
    except URLError:
        print("url error")
    print(v)
    
            
               