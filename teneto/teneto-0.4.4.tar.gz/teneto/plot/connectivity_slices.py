
import matplotlib.pyplot as pyplot

def make_pretty_ax(ax,xoffset=-0.01,yoffset=-0.01,xlabel=None,ylabel=None,yticklabels=None,xticklabels=None,title=None,legend=False,leftaxis='on',bottomaxis='on'): 
    if yticklabels is None: 
        yticklabels = [np.round(t,3) for t in ax.get_yticks()]
    if xticklabels is None: 
        xticklabels = [np.round(t,3) for t in ax.get_xticks()]
    if bottomaxis == 'on':
        ax.spines['bottom'].set_position(('axes', xoffset))
        ax.spines['bottom'].set_color('gray')
    else:
        ax.spines['bottom'].set_color('none')
    if leftaxis == 'on':
        ax.spines['left'].set_color('gray')
        ax.spines['left'].set_position(('axes', yoffset))
    else: 
        ax.spines['left'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    if ylabel: 
        ax.set_ylabel(ylabel, fontname='Montserrat', fontweight='regular',color='gray')
    if xlabel: 
        ax.set_xlabel(xlabel, fontname='Montserrat', fontweight='regular',color='gray')
    if title: 
        ax.set_title(title, fontname='Montserrat', fontweight='regular',color='gray')
    if leftaxis == 'on': 
        ax.set_yticklabels(yticklabels, fontname='Montserrat', fontweight='regular',color='gray')
    elif leftaxis == 'off': 
        ax.set_yticks([])
    if bottomaxis == 'on':
        ax.set_xticklabels(xticklabels, fontname='Montserrat', fontweight='regular',color='gray')
    elif bottomaxis == 'off': 
        ax.set_xticks([])
    if legend == True: 
        L = ax.legend(frameon=False)
        plt.setp(L.texts, fontname='Montserrat', fontweight='regular',color='gray')


def get_net_label_bar(ax,labels,width=2):
    # Assumes all network labels are grouped togehter
    labu, labidx = np.unique(labels,return_index=True)
    idorder = np.argsort(labidx)
    labu = labu[idorder]
    labidx = labidx[idorder]
    labidx = np.hstack([labidx,100])
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    ax.set_xlim(xlim[0]-width, xlim[1])
    ax.set_ylim(ylim[0]+width, ylim[1])
    cols = plt.cm.Set2(np.linspace(0,1,len(labu)))
    rect = []
    # x rectangles
    xstart = 0
    for n in range(len(labidx)-1): 
        rect.append(Rectangle((xstart, xlim[1]+width), labidx[n+1], -width))
        xstart = labidx[n+1]
    xstart = 0
    for n in range(len(labidx)-1): 
        rect.append(Rectangle((-width, xstart), width, labidx[n+1]))
        xstart = labidx[n+1]
    # y rectangles
    #rect.append(Rectangle((-width, 0), width, 50))
    #rect.append(Rectangle((-width, 50), width, 50))
    pc = PatchCollection(rect, edgecolor=None, facecolor=cols)
    return pc 

def plot_net_legend(ax,labels):
    # Assumes all network labels are grouped togehter
    width = 7
    height = 4
    spacing = 5
    pad = 0.5
    labu, labidx = np.unique(labels,return_index=True)
    idorder = np.argsort(labidx)
    labu = labu[idorder]
    labidx = labidx[idorder]
    labidx = np.hstack([labidx,100])
    ax.set_xlim(0, width*5)
    height_required = len(labu) * spacing
    ax.set_ylim(-height_required*pad, height_required+height_required*pad)
    cols = plt.cm.Set2(np.linspace(0,1,len(labu)))
    rect = []
    # x rectangles
    for i, y in enumerate(range(0,len(labu)*spacing,spacing)): 
        rect.append(Rectangle((0, y), width, height))
        ax.text(width+2,y+1.5,labu[i],fontname='Montserrat', fontweight='regular',color='gray')


def r

ax[i+1].imshow(Rtmp,cmap='RdBu_r',vmin=-1,vmax=0.9999)
make_pretty_ax(ax[i+1],0,0,title=sub + ' (postop)')

ax[i].add_collection(get_net_label_bar(ax[i],labels))
