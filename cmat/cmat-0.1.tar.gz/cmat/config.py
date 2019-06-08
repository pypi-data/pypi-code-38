



# Background for confusion matrix
fig_facecolor = '#f7f7f7'

# Heatmap colors for plotting
heatmap_cmap = 'Blues_r'
heatmap_edge_color = '#f7f7f7'
# Font color
heatmap_font_color = 'k'

# Try to get the matplotlib pyplot object, handle import error
def pyplot():
  try:
    import matplotlib.pyplot as plt 
    return plt
  except ImportError:
    raise ImportError( 'Could not get pyplot object: matplotlib is not installed' )
