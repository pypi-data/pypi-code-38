import pandas as pd
import folium
from folium.plugins import MarkerCluster
from folium.plugins import FastMarkerCluster

def poi_maps(dataframe, columns):
    map = folium.Map(
        location=[
            dataframe[columns[0]].mean(), 
            dataframe[columns[1]].mean()
            ], 
            zoom_start=4)
    mc = MarkerCluster()
    #creating a Marker for each point in df_sample. Each point will get a popup with their zip
    for row in dataframe.itertuples():
        mc.add_child(folium.Marker(location=[row.latitude,  row.longitude],
                     popup=row.name))
    map.add_child(mc)
    map
    return map