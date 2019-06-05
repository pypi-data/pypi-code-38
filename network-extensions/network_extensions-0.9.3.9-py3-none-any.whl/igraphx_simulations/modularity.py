from collections import  defaultdict
from network_extensions.igraphx import mergeAllGraphsIntervall
import igraph
import pandas

def setWeights(factor=1):
    C1=1
    C2=2
    C3=3
    P1=1*factor
    P2=2*factor
    P3=3*factor
    
    weights = {'http://ontologies.mpiwg-berlin.mpg.de/scholarlyRelations/acted_as_supervisor': C1,
     'http://ontologies.mpiwg-berlin.mpg.de/scholarlyRelations/co_author':C3,
     'http://ontologies.mpiwg-berlin.mpg.de/scholarlyRelations/collaborated':C3,
     'http://ontologies.mpiwg-berlin.mpg.de/scholarlyRelations/degree_at':P1,
     'http://ontologies.mpiwg-berlin.mpg.de/scholarlyRelations/director_at':P3,
     'http://ontologies.mpiwg-berlin.mpg.de/scholarlyRelations/edited_volume':P2,
     'http://ontologies.mpiwg-berlin.mpg.de/scholarlyRelations/had_phd_supervisor':C3,
     'http://ontologies.mpiwg-berlin.mpg.de/scholarlyRelations/influenced_by':C2,
     'http://ontologies.mpiwg-berlin.mpg.de/scholarlyRelations/leader_of':P3,
     'http://ontologies.mpiwg-berlin.mpg.de/scholarlyRelations/lecturer_at':P1,
     'http://ontologies.mpiwg-berlin.mpg.de/scholarlyRelations/member_of':P1,
     'http://ontologies.mpiwg-berlin.mpg.de/scholarlyRelations/phd_at':P1,
     'http://ontologies.mpiwg-berlin.mpg.de/scholarlyRelations/professor_at':P2,
     'http://ontologies.mpiwg-berlin.mpg.de/scholarlyRelations/researcher_at':P2,
     'http://ontologies.mpiwg-berlin.mpg.de/scholarlyRelations/student_at':P1,
     'http://ontologies.mpiwg-berlin.mpg.de/scholarlyRelations/undefined_relation':P1,
     'http://ontologies.mpiwg-berlin.mpg.de/scholarlyRelations/visiting_at':P1,
     'http://ontologies.mpiwg-berlin.mpg.de/scholarlyRelations/was_influencial':C2,
     'http://ontologies.mpiwg-berlin.mpg.de/scholarlyRelations/was_present_at':P1}
     
     
    return weights



def generateYearGraphsWithWeight(ynw,period,weightfactor,zeroDelete=True,tps=["w","wo"]):
    weights = setWeights(weightfactor)
    
    ynw_periods = defaultdict(dict)
    for t in tps:
        ynw_periods_t = mergeAllGraphsIntervall(ynw[t],period,mergeattr="name")
       
        for y,gr in ynw_periods_t.items():
            dels = 0
            for a,w in weights.items():
                sels = gr.es.select(typ=a)
                if w == 0:
                    dels+=len(sels)
                    if zeroDelete:
                        gr.delete_edges(sels)
                    else:
                        sels["weight"]=0
                else:
                    sels["weight"]=w
                #print(dels)
                
            ynw_periods[t][y] = {"graphs":gr,"largest_component":gr.components(mode=igraph.WEAK).giant()}

    return ynw_periods

def modularity_by_attribute(graphs,attr,attrMap,typ="graphs"):
    
    df = pandas.DataFrame()
    df["modularity_disc"] = pandas.Series(index=graphs.keys())
    df["modularity_disc_weight"] = pandas.Series(index=graphs.keys())
    for y,gr in graphs.items():
        
        gr = gr[typ]
        membs = igraph.VertexClustering(gr,membership=[attrMap[x.split(",")[0]] for x in gr.vs[attr]])
        membs = igraph.VertexClustering(gr,membership=[attrMap[x.split(",")[0]] for x in gr.vs[attr]])
    
        
        df["modularity_disc"][y] = gr.modularity(membs,weights=None)
        df["modularity_disc_weight"][y] = gr.modularity(membs,weights="weight")
     
        
        
    return df

def modularitySeries(ynw,period,weightfactor,attr,attrMap, func, func_cache, zeroDelete=True,tps=["w","wo"],typ="graphs",):
    ynw_periods = generateYearGraphsWithWeight(ynw, period, weightfactor, zeroDelete=zeroDelete, tps=tps)
    
    rets = {}
    for t in tps:
        
        for y,gr in ynw_periods[t].items():
            for n in gr[typ].vs:
                n[attr] = ",".join([x[0] for x in func(n["name"],func_cache)])
        
        
        df = modularity_by_attribute(ynw_periods[t],attr,attrMap,typ=typ)
        ret = {}
        ret["avg_mod"] = df["modularity_disc"].mean()
        ret["avg_mod_weight"] = df["modularity_disc_weight"].mean()
        
        ret["avg_max"] = df["modularity_disc"].max()
        ret["avg_max_weight"] = df["modularity_disc_weight"].max()
        
        rets[t] = ret
    
    return rets
    
    
    
    
    
