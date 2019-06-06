from collections import defaultdict
import igraph
import pandas
from itertools import product
import math
import logging


#TYPES = ["graphs","largest_component","undirected","largest_component_undirected","simplified","simplified_undirected"]

logger = logging.getLogger(__name__)

STANDARD_PROPS = ["no_nodes","no_edges",
                  "no_nodes_div_edges",
                  "density","average_path_length",
                  "transitivity_undirected","radius"]
SIM_METHODS = ["Erdos_Renyi","Barabasi"]

def calculate_mean_values(simulations,typs = ["graphs","largest_component"]):
    for typ in typs:
        for sim,properties in simulations["properties"][typ].items():
            for p in properties:
                try:
                    properties["mean_%s"%p] = [numpy.mean(x) for x in properties[p]]
                    properties["std_%s"%p] = [numpy.std(x) for x in properties[p]]
                except KeyError:
                    print(properties)
                    raise KeyError


def calculate_diffs(simulations,graphproperties,typs = ["graphs","largest_component"]):
    """
    Calculate the difference (difference and quotient of real value and simulations.
    Returns the means difference over the whole time period.
    The differences are added to the graph properties
    :param simulations: Results of simulations
    :param graphproperties: Values of the year graphs for some properties, differences and quotient will be added here!
    :param typs: (optional) defaults to "graphs" and "largest component"
    :param props: (options) props to be calculates defaults to ["no_nodes","no_edges","no_nodes_div_edges"]
    :return:
    """
    retV = {}
    for typ in typs:
        rets =defaultdict(dict)
        for sim,properties in simulations["properties"][typ].items():
            for p in properties:
                try:
                    properties["div_%s"%p] = graphproperties[typ][p]/properties["mean_%s"%p]
                    properties["diff_%s"%p] = (graphproperties[typ][p]-properties["mean_%s"%p])/properties["mean_%s"%p]
               
                    rets[sim][p] = math.sqrt((properties["diff_%s"%p]**2).sum())/len(properties["mean_%s"%p])
                    rets[sim][p+"_mean"] = graphproperties[typ][p].mean()
                    rets[sim][p+"_mean_sim"] = properties["mean_%s"%p].mean()
                except KeyError:
                    pass # should be ignored, can happen if p is a calculated mean_
                
        retV[typ]=rets      
    return retV
            
            


def calculate_edge_node_functions(simulations,graphproperties = None):
    for graphs_set in ["graphs","largest_component"]:
        for sim_name,simulation in simulations[graphs_set].items():  
            graphproperties = simulations["properties"][graphs_set][sim_name] # dataframe mit allen properties für dieses Simulations  (columns = index = years)
           
            graphproperties["no_nodes"] = pandas.Series(index=graphproperties.index,dtype=object)
            graphproperties["no_edges"] = pandas.Series(index=graphproperties.index,dtype=object)
            graphproperties["no_nodes_div_edges"] = pandas.Series(index=graphproperties.index,dtype=object)
            for y,gr_its in simulations[graphs_set][sim_name].items():          
               
                graphproperties["no_nodes"].loc[y] = numpy.empty(len(gr_its))#pandas.Series(index=list(range(0,len(gr_its))))
                graphproperties["no_edges"].loc[y] =  numpy.empty(len(gr_its))#pandas.Series(index=range(0,len(gr_its)))

                for gr_index in range(len(gr_its)): #durch alle iterationen
                    gr = gr_its[gr_index]
                    
                    graphproperties["no_nodes"].loc[y][gr_index] = len(gr.vs)
                    graphproperties["no_edges"].loc[y][gr_index] = len(gr.es)
                 
                graphproperties["no_nodes_div_edges"].loc[y]= graphproperties["no_nodes"].loc[y]/ graphproperties["no_edges"].loc[y]
    
def simulate_largest_components(ynw,typ=None,iterations=10):
    """this method takes a year-network and creates - simular graphs with Erdos_Renyi and Barabasi
    and returns yeargraphs for both cases and the development of some graph properties
    (no of nodes and no of edges)
    """
    simulations=defaultdict(dict)
    for it in range(iterations):
        arb_er = {}
        lc_er = {}

        for y,graph in ynw.items():    
                arb_er[y] = igraph.Graph.Erdos_Renyi(len(graph.vs),m=len(graph.es))
                lc_er[y] = arb_er[y].components(mode=igraph.WEAK).giant()
            
        simulations["Erdos_Renyi"][it]={"graph":arb_er.copy(),
                                         "largest_component":lc_er.copy()
                                         #"graphproperties":pandas.DataFrame()
                                         }

        arb = {}
        lc = {}
        for y, graph in ynw.items():
            if graph.is_directed():
                arb[y] = igraph.Graph.Barabasi(len(graph.vs), graph.vs.degree(mode = igraph.OUT),directed=True)
            else:
                arb[y] = igraph.Graph.Barabasi(len(graph.vs), graph.vs.degree())

            lc[y] = arb[y].components(mode=igraph.WEAK).giant()

        simulations["Barabasi"][it] = {"graph": arb.copy(),
                                       "largest_component": lc.copy()
                                       #"graphproperties": pandas.DataFrame()
                                       }
    return simulations



def addProperty(graphproperties_all,func,graphs,params=None,kwargs={},
                simulations = None,
                reset=False):

    ##simulations = simulations[graph_type]["Barbasi"][it][graph|largest_component|graphproperties][y]
    if simulations is None:
        logger.error("simulations must not be none!")
        raise ValueError

    simulations_in = simulations

    # first the values for the original graphs
    for graph_type,graph_y in graphs.items():
        for y,graph in graph_y.items():
            for gr_tp in ["graph","largest_component"]:
                if gr_tp == "largest_component":
                    gr_tmp = graph.components(mode=igraph.WEAK).giant()
                else:
                    gr_tmp = graph

                if func == "no_nodes":
                    val = len(gr_tmp.vs)
                elif func == "no_edges":
                    val = len(gr_tmp.es)
                else:
                    val = getattr(gr_tmp, func)(params, **kwargs)

                addToDataFrame(graphproperties_all[graph_type]["original"],"%s_%s"%(gr_tp,func),y,val)

    #now the simulations
    for graph_type,simulation in simulations_in.items(): # is
        #grp_it = pandas.DataFrame(columns=SIM_METHODS,index = range(1900,200))
        graphproperties_subgraph = graphproperties_all[graph_type]
        if func in graphproperties_subgraph and not reset:
            continue

        #graphproperties = graphproperties.transpose()
        #graphproperties[func] = pandas.Series(index=graphproperties.index)
        for sim_type,graphs_it in simulation.items():
            grp_it = defaultdict(lambda: defaultdict(list))
            # initialize grp_it
            #for gt in graphs_it[0].keys():
             #   for y in range(1900, 2000):  # todo get years from somewhere
             #       grp_it[gt][y] = []

            for it,graph_type_graph in graphs_it.items():

                for graph_type_simulation,gra in graph_type_graph.items():
                    for y,graph in gra.items():
                            if func == "no_nodes":
                                    val = len(graph.vs)
                            elif func == "no_edges":
                                val = len(graph.es)
                            else:
                                val = getattr(graph,func)(params,**kwargs)
                            #addToDataFrame(graphproperties_subgraph,"%s_%s_%s"%(sim_sub_graph_type,graph_type,func),y,val)
                            grp_it[graph_type_simulation][y].append(val)
                            #print(grp_it)
            #now we add the mean of simulations to the properties
            for gt_simulation,val_y in grp_it.items():
                for y,val in val_y.items():
                    val = numpy.mean(val)
                    addToDataFrame(graphproperties_subgraph[sim_type],"%s_%s"%(gt_simulation,func),y,val)

    return
                    
def addToDataFrame(df,c,i,v):
    if not c in df:
        df[c] = pandas.Series()
    df.loc[i,c] = v


import numpy
def addPropertyMean(simulations,func,name=None,typs=["graphs","largest_component"],reset=False,params=None,kwargs={}): 
        if name is not None:
                name = func+"_%s"%name
        else:
                name = func
        for typ in typs:
     
            for t,sim in simulations[typ].items():
                if "%s"%name in simulations["properties"][typ][t] and not reset:
                    print("cached")
                    continue
                    
                
                #simulations["properties"][typ][t]["%s"%name] = pandas.Series(index=simulations["properties"][typ][t].index,dtype=object)
                simulations["properties"][typ][t]["%s"%name] = pandas.Series(index=simulations["properties"][typ][t].index,dtype=object)
                for y,grs in sim.items():
                    #graphsIteration = 
                    val = []
                    for gr in grs:
                        val.append(getattr(gr,func)(params,**kwargs))         
    
                    simulations["properties"][typ][t]["%s"%name][y]=numpy.mean(val)
                   
     