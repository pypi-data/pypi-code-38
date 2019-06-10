from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.colors import LightSource
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt
from random import choice
import scipy.linalg
from pylab import *
import numpy as np
import math
import re

#get information from .dat document
def getinfo(inputpath):
    
    data = open(inputpath,'r')
    compound_list = []
    known = False
    
    for line in data:
        if not line == '\n':
            if re.findall('Content A:', line):
                content_A = re.findall('(?<=: )\w+', line)[0]
                continue
            if re.findall('Content B:', line):
                content_B = re.findall('(?<=: )\w+', line)[0]
                continue
            if re.findall('Content C:', line):
                content_C = re.findall('(?<=: )\w+', line)[0]
                continue
            if re.findall('Content D:', line):
                content_D = re.findall('(?<=: )\w+', line)[0]
                continue 
            if re.findall('Figure name:', line):
                figure_name = re.findall('(?<=: ).+', line)[0]
                continue
            if re.findall('#Known compounds:', line):
                known = True
                continue
            if known:
                compound_list.append(re.findall('[\w()]+', line)[0])
                continue
           
    content_list = [content_A, content_B, content_C, content_D]    
    data.close()
    
    return content_list, figure_name,  compound_list

#generate tick
#def generate_tick(length):
#    
#    x_change = length * sin30
#    y_change = length * cos30
#
#    for x in np.arange(0.5, 1.01, 0.05):
#        ax.plot([x, x + length], [(1 - x) * tan60, (1 - x) * tan60], [z_min, z_min], color = 'red', linewidth = 0.5)
#    for (x1, x2) in zip(np.arange(0.55, 1, 0.05), np.arange(0.45, 0, -0.05)):
#        ax.plot([x1, x2], [(1 - x1) * tan60, (1 - x1) * tan60], [z_min, z_min], color = 'red', linestyle = ':', linewidth = 0.5)
#    for x in np.arange(0, 0.51, 0.05):
#        ax.plot([x, x - x_change], [x * tan60, x * tan60 + y_change], [z_min, z_min], color = 'green', linewidth = 0.5)
#    for (x1, x2) in zip(np.arange(0, 0.5, 0.05), np.arange(0, 1, 0.1)):
#        ax.plot([x1, x2], [x1 * tan60, 0], [z_min, z_min], color = 'green', linestyle = ':', linewidth = 0.5)
#    for x in np.arange(0, 1.01, 0.1):
#        ax.plot([x, x - x_change], [0, -y_change], [z_min, z_min], color = 'blue', linewidth = 0.5)
#    for (x1, x2) in zip(np.arange(0.1, 1, 0.1), np.arange(0.55, 1, 0.05)):
#        ax.plot([x1, x2], [0, (1 - x2) * tan60], [z_min, z_min], color = 'blue', linestyle = ':', linewidth = 0.5)

#get coordinate from compounds information
def coordinate(compound_list):

    x_list, y_list, z_list = [], [], []
    
    for compound in compound_list:
        content_dict = {}
        for i in content_list:
            if re.findall('%s' % i, compound):
                if re.findall('(?<=%s)\)?[0-9]+' % i, compound):
                    content_dict[i] = re.findall('[0-9]+', re.findall('(?<=%s)\)?[0-9]+' % i, compound)[0])[0]
                else:
                    content_dict[i] = '1'
            else:
                content_dict[i] = '0'
                
        percent_B = float(content_dict[content_list[1]]) / (float(content_dict[content_list[0]]) + float(content_dict[content_list[1]]) + float(content_dict[content_list[2]]) + float(content_dict[content_list[3]]))
        percent_C = float(content_dict[content_list[2]]) / (float(content_dict[content_list[0]]) + float(content_dict[content_list[1]]) + float(content_dict[content_list[2]]) + float(content_dict[content_list[3]]))
        percent_D = float(content_dict[content_list[3]]) / (float(content_dict[content_list[0]]) + float(content_dict[content_list[1]]) + float(content_dict[content_list[2]]) + float(content_dict[content_list[3]]))
        x = percent_C * sin30 + percent_B + percent_D * sin30
        x_list.append(x)
        y = percent_D * math.sqrt(3) / 6 + percent_C *  math.sqrt(3) / 2
        y_list.append(y)
        z = percent_D * math.sqrt(6) / 3
        z_list.append(z)
        
    return x_list, y_list, z_list

#label with compound names
def label(x_list, y_list, z_list, compound_list):
    
    for x, y, z, name in zip(x_list, y_list, z_list, compound_list):
        ax.text(x, y, z, name, fontsize = 9)
        horizontalalignment = 'center'
        
#plot graph
def plotgraph(compound_list):

    x_list, y_list, z_list = coordinate(compound_list)
    label(x_list, y_list, z_list, compound_list)
    for x, y, z in zip(x_list, y_list, z_list):
        ax.scatter(x, y, z, c = 'red', marker = 'o', linewidth = 1)
         
#basic info.   
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
tan60 = math.tan(math.pi/3)
sin30 = math.sin(math.pi/6)
cos30 = math.cos(math.pi/6)
tan30 = math.tan(math.pi/6)
sin45 = math.sin(math.pi/4)
sin15 = math.sin(math.pi/12)
cos15 = math.cos(math.pi/12)
height = math.sqrt(1 - square(cos30 * 2 / 3))

#the list of all colors
colors = []
for cname in matplotlib.colors.cnames:
    colors.append(cname)
    
#use compounds imformation to plot graph   
content_list, figure_name, compound_list = getinfo('./test-terta.dat')
plotgraph(compound_list)

#plotgraph()
ax.text2D(0.5, 0.95, figure_name, transform=ax.transAxes)

#hide axises
ax.w_yaxis.line.set_lw(0.)
ax.set_yticks([])
ax.w_xaxis.line.set_lw(0.)
ax.set_xticks([])
ax.w_zaxis.line.set_lw(0.)
ax.set_zticks([])

#plt.gca().invert_zaxis()
ax.set_xlim(0, 1)
ax.set_ylim(0, cos30)
ax.set_zlim(0, height)

#generate the tetrahedron
ax.plot([0, 0.5], [0, cos30], [0, 0], color = 'black')
ax.plot([0.5, 1], [cos30, 0], [0, 0], color = 'black')
ax.plot([0, 1], [0, 0], [0, 0], color = 'black')
ax.plot([0, 0.5], [0, cos30 / 3], [0, height], color = 'black')
ax.plot([0.5, 0.5], [cos30, cos30 / 3], [0, height], color = 'black')
ax.plot([1, 0.5], [0, cos30 / 3], [0, height], color = 'black')
for x in np.arange(0.2, 1.0, 0.2):
    ax.plot([x, x + sin30 * (1 - x)], [0, (1 - x) * cos30], [0, 0], linestyle = ':', linewidth = 1, color = 'grey')
    ax.plot([x, x - sin30 * x], [0, x * cos30], [0, 0], linestyle = ':', linewidth = 1, color = 'grey')
    ax.plot([x, sin30 * x], [0, x * math.sqrt(3) / 6], [0, x * height], linestyle = ':', linewidth = 1, color = 'grey')
    ax.plot([x, x + sin30 * (1 - x)], [0, (1 - x) * math.sqrt(3) / 6], [0, (1 - x) * height], linestyle = ':', linewidth = 1, color = 'grey')
    ax.plot([x * sin30, 1 - x * sin30], [x * cos30, x * cos30], [0, 0], linestyle = ':', linewidth = 1, color = 'grey')
    ax.plot([x * sin30, 1 - x * sin30], [ x * math.sqrt(3) / 6,  x * math.sqrt(3) / 6], [x * height, x * height], linestyle = ':', linewidth = 1, color = 'grey')
    ax.plot([x * sin30, x * sin30], [x * cos30, x * math.sqrt(3) / 6], [0, x * height], linestyle = ':', linewidth = 1, color = 'grey')
    ax.plot([x * sin30, 0.5], [x * cos30, cos30 - (1 - x) * math.sqrt(3) / 3], [0, (1 - x) * height], linestyle = ':', linewidth = 1, color = 'grey')
    ax.plot([(1 - x) * sin30, 0.5], [(1 - x) * math.sqrt(3) / 6, cos30 - (1 - x) * math.sqrt(3) / 3], [(1 - x) * height, (1 - x) * height], linestyle = ':', linewidth = 1, color = 'grey')
    ax.plot([1 - x * sin30, 0.5], [x * cos30, cos30 - (1 - x) * math.sqrt(3) / 3], [0, (1 - x) * height], linestyle = ':', linewidth = 1, color = 'grey')
    ax.plot([1 - x * sin30, 1 - x * sin30], [x * cos30, x * math.sqrt(3) / 6], [0, x * height], linestyle = ':', linewidth = 1, color = 'grey')
    ax.plot([0.5, 1 - x * sin30], [cos30 - x * math.sqrt(3) / 3, x * math.sqrt(3) / 6], [x * height, x * height], linestyle = ':', linewidth = 1, color = 'grey')
    
#generate_tick(0.02)
ax.text(-0.1, 0, -0.1, content_list[0], color = 'black', horizontalalignment = 'center')
ax.text(1.1, 0, -0.1, content_list[1], color = 'black', horizontalalignment = 'center')
ax.text(0.5, cos30 + 0.1, -0.1, content_list[2], color = 'black', horizontalalignment = 'center')
ax.text(0.5, math.sqrt(3) / 6, height + 0.1, content_list[3], color='black', horizontalalignment = 'center')
 
#for x in np.arange(0, 1.01, 0.1):
#    ax.text(x - 0.05, -0.1, 0, int(x * 100), (-0.5, cos30, 0), color = 'blue',fontsize = 10)
#for x in np.arange(0.5, 1.04, 0.05):
#    ax.text(x + 0.05, (1 - x) * tan60, 0, int(200 - int(200 * x)), color = 'red',fontsize = 10)
#for x in np.arange(0, 0.501, 0.05):
#    ax.text(x - 0.1, x * tan60 + 0.05, 0, int(100 - x * 200), (-0.5, cos30, 0), color = 'green',fontsize = 10)

#ax.plot([0.2, 0.8], [-0.15, -0.15], [0, 0], color = 'blue')
#ax.plot([0.8, 0.8 - 0.02 * sin45], [-0.15, -0.15 - 0.02 * sin45], [0, 0], color = 'blue')
#ax.plot([0.8, 0.8 - 0.02 * sin45], [-0.15, -0.15 + 0.02 * sin45], [0, 0], color = 'blue')
#ax.plot([0.6 + 0.15 * cos30, 0.9 + 0.15 * cos30], [0.4 * tan60 + 0.15 * sin30, 0.1 * tan60 + 0.15 * sin30], [0, 0], color = 'red')
#ax.plot([0.6 + 0.15 * cos30, 0.6 + 0.15 * cos30 + 0.02 * cos15], [0.4 * tan60 + 0.15 * sin30, 0.4 * tan60 + 0.15 * sin30 - 0.02 * sin15], [0, 0], color = 'red')
#ax.plot([0.6 + 0.15 * cos30, 0.6 + 0.15 * cos30 - 0.02 * sin15], [0.4 * tan60 + 0.15 * sin30, 0.4 * tan60 + 0.15 * sin30 - 0.02 * cos15], [0, 0], color = 'red')
#ax.plot([0.1 - 0.15 * cos30, 0.4 - 0.15 * cos30], [0.1 * tan60 + 0.15 * sin30, 0.4 * tan60 + 0.15 * sin30], [0, 0], color = 'green')
#ax.plot([0.1 - 0.15 * cos30, 0.1 - 0.15 * cos30 + 0.02 * cos15], [0.1 * tan60 + 0.15 * sin30, 0.1 * tan60 + 0.15 * sin30 + 0.02 * sin15], [0, 0], color = 'green')
#ax.plot([0.1 - 0.15 * cos30, 0.1 - 0.15 * cos30 - 0.02 * sin15], [0.1 * tan60 + 0.15 * sin30, 0.1 * tan60 + 0.15 * sin30 + 0.02 * cos15], [0, 0], color = 'green')

plt.show()
    




