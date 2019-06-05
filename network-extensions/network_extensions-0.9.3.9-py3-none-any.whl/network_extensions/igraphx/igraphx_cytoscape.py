""" Methoden die den Gephi-Streaming-Möglichkeiten erweitern"""

# color all edges:
import time
import progressbar
import logging
from urllib.error import URLError
from _collections import defaultdict
logger = logging.getLogger(__name__)


from py2cytoscape.data.cyrest_client import CyRestClient
from py2cytoscape.data.util_network import NetworkUtil as util
from py2cytoscape.data.style import StyleUtil as s_util
import pandas
import pylab
import matplotlib

class MessageCache:
    """singleton wird benutzt um berechnete Graphdaten zu cachen"""
    class __MessageCache:  
        messages={}
        
        def write(self,urn,txt):
            oldtxt = self.messages.get(urn,"")
            self.messages[urn]=oldtxt+txt
            
    
    instance = None
    def __init__(self):
        if not MessageCache.instance:
            MessageCache.instance = MessageCache.__MessageCache()
            
    def __getattr__(self, name):
        return getattr(self.instance, name)

def setconcat(vals):
    val_con = set(vals)
    return ",".join(list(val_con))

class CytoscapeStreamerExtension(object):
    def __init__(self,cy,gr_all,ident_attr=None,simplify=True,name=None):
        """:param CyRestClient cy:
           :param  Graph gr_all:
           :param  str ident_attr: Name des Vertex-Attributes, das eine eindeutige Zuordnung ermöglicht
           
        """     
        self.cy= cy
        self.gr_all = gr_all
        if simplify:
            self.gr_all=self.gr_all.simplify(combine_edges=dict(begin=min,end=max,label=setconcat,sek=setconcat,typ=setconcat))
        
        if "id" in gr_all.vs.attributes():
            gr_all.vs["id_local"]=gr_all.vs["id"].copy()
            gr_all.es["id_local"]=["e%s"%s for s in range(0,len(gr_all.es))]
            del gr_all.vs["id"] #graph should not have an id field
        self.g_cy = cy.network.create_from_igraph(gr_all,name=name)
        #self.g_cy.session.post(self.g_cy.get_url()+"views")
        self.ident_attr = ident_attr 
        try:
            self.persins = list(gr_all.vs[ident_attr])
        except:
            pass
    
        my_style = cy.style.create('MPIWG',original_style="Sample2")   
        #my_style.create_passthrough_mapping(column="show_label",
        #                                    col_type="String",
        #                                   vp="NODE_LABEL")
        cy.style.apply(style=my_style, network=self.g_cy)
        mv = self.g_cy.get_views()
        self.view=self.g_cy.get_view(mv[0],format="view")
        self.nodeColorMap={}
        self.colorNodeAttribute=None
        self.style = my_style
        
    def setColorMap(self,colorNodeAttribute,colormap_sytle="Vega20"):
        clrs = self.gr_all.vs[colorNodeAttribute]
        self.colorNodeAttribute=colorNodeAttribute
        colorAttributes = list(set(clrs)) #uniquelist
        cmap = pylab.get_cmap('Vega20', len(colorAttributes))    # PiYG
        for i in range(cmap.N):
            rgb = cmap(i)[:3] # will return rgba, we take only first 3 so we get rgb
            self.nodeColorMap[colorAttributes[i]]=matplotlib.colors.rgb2hex(rgb)
            
        
    def showAll(self,layout=None):
        """
        Schicke den gesamten Graphen an Cytoscape
        :param Layout (optional) layout: Cytoscape layout default fruchterman_reingold
        """
        if layout is None:
            l = self.gr_all.layout_fruchterman_reingold()
        else:
            l = layout
            
       
        nodes = self.g_cy.get_nodes()
        locations=[[nodes[i],(l[i][0]+30)*6,(l[i][1]+30)*6] for i in range(0,len(nodes))]
        
        self.cy.layout.apply_from_presets(self.g_cy, positions=locations)
        #self.cy.style.update_defaults({"EDGE_WIDTH":5.})
        change_df=pandas.DataFrame(index=nodes,columns=["NODE_FILL_COLOR"])
        
        if self.colorNodeAttribute is not None:
            for suid,n in zip(nodes,self.gr_all.vs):
                change_df.loc[suid]=[self.nodeColorMap[n[self.colorNodeAttribute]]]
        else:
            change_df = change_df.fillna("#0000FF")
            
        self.primaryNodeColors=change_df
        self.view.batch_update_node_views(change_df)
        #self.cy.layout.bundle_edge(self.g_cy)
        
    def deleteAll(self):
        """loesche alle Knoten"""     
        self.cy.session.delete()

    def setForAllNode(self,vals):
        """setze Attribute für alle Knoten
        :param dict vals: Dictionary, dass an die Knoten übergeben wird. 
        """
        logger.debug("setting")
        nt = self.g_cy.get_node_table()
        for k,v in vals.items():
            nt[k] = v
        
        logger.debug("setting2")
        self.g_cy.update_node_table(nt,data_key_col="id_local",network_key_col="id_local")
        logger.debug("setting3")
        
    def setForAllEdges(self,vals={"r":0.8,"g":0.8,"b":0.8}):
        """setze Attribute für alle Kanten
        :param dict vals: Dictionary, dass an die Kanten übergeben wird. 
        """
        return
        en_all={}
          
        nt = self.g_cy.get_edge_table()
        for k,v in vals.items():
            nt[k] = v
        
        set.g_cy.update_edge_table(nt,data_key_col="BEND_MAP_ID",network_key_col="BEND_MAP_ID")
        
        
    def streamNodes(self,graphs,nodes_attr,displayattr,intervall=1,sleep_time=0,
                    stream=True,
                    year_cn=None,
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
        
        :returns: streamer events
        """
        id_att2suid = util.name2suid(self.g_cy,id_attr=displayattr)
        self.g_cy.add_node("YEAR")  
       
        if messages_urn is not None:
            messages = MessageCache()
    
        #nt = self.g_cy.get_node_table()
     
        if year_cn is not None:
            for year,changes in graphs.keys():
                if stream: 
                        self.view.batch_update_node_views(changes)                         
                        
             
        else:
            year_cn={}
            gr_all_ls = list(self.gr_all.vs) #alle knoten
            for year,gr in graphs.items():
                if year%intervall !=0:
                    continue
                
                if messages_urn is not None:
                    messages.write(messages_urn,"<p>Calculating year: %s</p>"%year)
                logger.info("year: %s"%year)
                time.sleep(sleep_time)
                #changes = defaultdict(dict)
                change_df=pandas.DataFrame(columns=["NODE_SIZE",
                                                   "NODE_LABEL",
                                                   "NODE_FILL_COLOR",
                                                   'NODE_LABEL_FONT_SIZE',
                                                   "NODE_LABEL_WIDTH",
                                                   'NODE_LABEL_FONT_FACE']
)
                #stream.post(gr,cnt)
                bw=nodes_attr.get(year,nodes_attr.get(str(year)))
                vals={}
                for b in bw:
                    vals[b[0][0]]=(b[0][1],b[1]) #betweenes und rang
                for v in gr_all_ls:
                   
                    id_att = v[displayattr]
                    suid = id_att2suid[id_att]
                    
                    if id_att in vals.keys(): #gibt es den Namen unter den Top 10  
               
                        change_df.loc[suid]=[5+min(5,vals[id_att][1]/3),id_att,"#FF3333",50,200,'SansSerif,plain,50']
                        #changes["NODE_SIZE"][id_att]=5+min(5,vals[id_att][1]/20)
                        #changes["NODE_LABEL"][id_att]=id_att
                        #changes["NODE_FILL_COLOR"][id_att]="#FF3333"
                        

                    else:
                        change_df.loc[suid]=[1,"",self.primaryNodeColors.loc[suid]["NODE_FILL_COLOR"],0,0,""]
                        #changes["NODE_SIZE"][id_att]=1
                        #changes["NODE_LABEL"][id_att]=""
                        #changes["NODE_FILL_COLOR"][id_att]="#3333FF"
                        

                    
                        
                #stream.post(gr_tmp,cnt)
                #cn["YEAR"]={"label":year, "size":400, "r":0,"g":1,"b":0}
                         
                if stream: 
                    if messages_urn is not None:
                        messages.write(messages_urn,"<p>Streaming year: %s</p>"%year)
                    self.view.batch_update_node_views(change_df)
                    #for prop,vals in changes.items():                              
#                         self.view.update_node_views(visual_property=prop,
#                                                    values=vals,
#                                                    key_type=displayattr)
                year_cn[year]=change_df
            
        return year_cn
    
    
    def showYears(self,
                    graphs,
                    nodes_attr,
                    displayattr,
                    intervall=1,
                    sleep_time=0,
                    layouts={},
                    stream=True,
                    year_cn=None,
                    year_en=None,
                    messages_urn=None):
        
        for year in graphs.keys():
                if year%intervall !=0:
                    continue
                
                    gr = graphs[year]
                    
                    
                    layout = layouts.get(year,None)
                    if layout is None:
                        l = gr.layout_fruchterman_reingold()
                    else:
                        l = layout
                        
                   
                    nodes = gr.get_nodes()
                    locations=[[nodes[i],(l[i][0]+30)*6,(l[i][1]+30)*6] for i in range(0,len(nodes))]
                    
                    self.cy.layout.apply_from_presets(self.g_cy, positions=locations)
                    self.style.update_defaults({"EDGE_WIDTH":5.})
                    change_df=pandas.DataFrame(columns=["NODE_FILL_COLOR"])
                    
                    if self.colorNodeAttribute is not None:
                        for suid,n in zip(nodes,self.gr_all.vs):
                            change_df.loc[suid]=[self.nodeColorMap[n[self.colorNodeAttribute]]]
                            
                        
                        self.primaryNodeColors=change_df
                        self.view.batch_update_node_views(change_df)
                    #self.cy.layout.bundle_edge(self.g_cy)
                    
                
    def streamEdges(self,
                    graphs,
                    nodes_attr,
                    displayattr,
                    intervall=1,
                    sleep_time=0,
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
        
        :returns: streamer events pro yeary
        """
        en = self.g_cy.get_edge_table()
        #self.g_cy.create_edge_column("color")
        edge2suid=defaultdict(set)
        
        reset=pandas.DataFrame(index=en.index,columns=["EDGE_SOURCE_ARROW_UNSELECTED_PAINT",
                               "EDGE_STROKE_UNSELECTED_PAINT",
                               "EDGE_TARGET_ARROW_UNSELECTED_PAINT",
                               "EDGE_SOURCE_ARROW_SELECTED_PAINT",
                               "EDGE_STROKE_SELECTED_PAINT",
                               "EDGE_TARGET_ARROW_SELECTED_PAINT"])
                               #"EDGE_WIDTH"])
       
        edge = pandas.DataFrame(index=en.index,columns=["EDGE_WIDTH"])
        edge = edge.fillna(5.)
        
        main_color ="#AAAAAA"
        
        reset=reset.fillna(main_color)
        reset = reset.join(edge)
     
        #reset_list=[main_color for j in range(0,6)]+[50]
        for i,c in en.iterrows():
            #print(i)
            edge2suid[(c["source"],c["target"])].add(i)
            
            #reset.loc[i]=reset_list
        if messages_urn is not None:
            messages = MessageCache()
    
            messages.write(messages_urn,"<p>set color for edges</p>")
               
        logger.debug("set color for edges")
        
      
            
        logger.info("RESET")                
        self.view.batch_update_edge_views(reset)
        logger.info("RESETTED")  
        
        
        #en["color"]="0"
        if year_cn is None and year_en is None:
            logger.info("no nodes")
            if messages_urn is not None:
                messages.write(messages_urn,"<p>no nodes</p>")
        
            year_cn=self.streamNodes(graphs, nodes_attr, displayattr,intervall, sleep_time, False,messages_urn=messages_urn)
            logger.info("--created")
         
        if year_en is not None:
            for year in graphs.keys():
                if year%intervall !=0:
                    continue
                
                if stream: 
                    if messages_urn is not None:
                        messages.write(messages_urn,"<p>Streaming:%s</p>\n"%year)
                    self.view.batch_update_node_views(year_en[year][0])
                    self.view.batch_update_edge_views(year_en[year][1])
                    
                   
        
        else:           
            year_en={}
            for year,gr in graphs.items():
                if year%intervall !=0:
                    continue
                
                if messages_urn is not None:
                    messages.write(messages_urn,"<p>Streaming:%s</p>\n"%year)
                    
                logger.info(year)
                self.setForAllEdges() # alle Kanten auf Grau
                time.sleep(sleep_time)
                cn=year_cn[year]
                #changes = defaultdict(dict)
                changes_df = pandas.DataFrame(columns=["EDGE_SOURCE_ARROW_UNSELECTED_PAINT",
                                                       "EDGE_STROKE_UNSELECTED_PAINT",
                                                       "EDGE_TARGET_ARROW_UNSELECTED_PAINT",
                                                       "EDGE_SOURCE_ARROW_SELECTED_PAINT",
                                                       "EDGE_STROKE_SELECTED_PAINT",
                                                       "EDGE_TARGET_ARROW_SELECTED_PAINT",
                                                       "EDGE_WIDTH"])
                for e in gr.es:
                    
                    s=gr.vs[e.source][displayattr]
                    t=gr.vs[e.target][displayattr]
                    
                    
                    s_id=self.persins.index(s)
                    t_id=self.persins.index(t)
                    
                    suids = edge2suid[(s_id,t_id)]
                    
                    for suid in suids:
                        changes_df.loc[suid]=["#FF0000","#FF0000","#FF0000","#FF0000","#FF0000","#FF0000",5.]
    
                  
                #cn["YEAR"]={"label":year, "size":400, "r":0,"g":1,"b":0}
                
                if stream:
                    self.view.batch_update_node_views(cn)
                    self.view.batch_update_edge_views(changes_df)
                    
                year_en[year]=(cn,changes_df)
                
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
    import re
    import tarfile
    import igraph
    import sys
    import os

    
    from network_extensions import igraphx
    from dataverseTools import handleDataverse
    logger = logging.getLogger(__name__)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # add formatter to ch
    ch.setFormatter(formatter)

# add ch to logger
    logger.addHandler(ch)
    
    print(logger.getEffectiveLevel())
    print(logging.DEBUG)
    logger.info("logging start")
    
    dv = handleDataverse.DataverseHandler("datastore-dev.mpiwg-berlin.mpg.de",
                                          "c4cacadd-d3ac-45f0-94b9-98d5396e302b",
                                         "gmpg-astronomy-gremien")
    current_setting = settings["pers_pers_by_membership"]
    content = dv.getContent(current_setting["doi_all"],current_setting["graph_all_file"])
    with open("tmp.graphml","wb") as outf:
        outf.write(content.read())
    gr_all = igraph.load(open("tmp.graphml","rb"))
    
    #dv_gephi_url="http://localhost:8080/workspace1"
    
    # Create Client
    cy = CyRestClient()
    # Clear current session
    cy.session.delete()
   
    gse = CytoscapeStreamerExtension(cy,gr_all,current_setting["ident_attr"])
    logger.info("load graphs")
    content = dv.getContent(current_setting["doi"],current_setting["graph_file"])
    
    graphs = igraphx.getGraphsFromFile(content,current_setting["file_pattern"])
    logger.info("loaded graphs")
    try:
        gse.setColorMap(colorNodeAttribute="block_4")
        gse.showAll() 
        gse.setForAllNode({"label":""})
        logger.info("calc tops")
        pb = progressbar.ProgressBar()
        pb.start()
        #graphs = {k:v for k,v in graphs.items() if k < 1952}
        betw_years = igraphx.calcTopsForYears(graphs,
                                              max_len=10,
                                              displayAttr=current_setting["ident_attr"],
                                              progressBar=pb,
                                              displayAttr2="id_local",
                                              func="betweenness")
        logger.info("start streaming")
        
        #v = gse.streamNodes(graphs, betw_years,current_setting["ident_attr"])
        v = gse.streamEdges(graphs, betw_years,current_setting["ident_attr"])
    except URLError:
        logger.error("url error")
    #print(v)
    
            
               