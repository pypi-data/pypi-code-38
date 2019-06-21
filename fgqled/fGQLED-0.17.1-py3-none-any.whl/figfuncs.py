def formatFigure(ax, projection='2d', labels={'xlabel': '', 'ylabel': '', 'zlabel': ''}, fontsize=14, tickseparationx=2, tickseparationy=2, tickoffsetx=0, tickoffsety=0, ticksize=14):

    if projection == '2d':
        if 'xlabel' in labels.keys():
            xlabel = labels['xlabel']
            ax.set_xlabel(xlabel, fontsize=fontsize)
        if 'ylabel' in labels.keys():
            ylabel = labels['ylabel']
            ax.set_ylabel(ylabel, fontsize=fontsize)

        for ii, tick in enumerate(ax.yaxis.get_major_ticks()):
            tick.label.set_fontsize(ticksize)
            if (ii+tickoffsety) % tickseparationy != 0:
                tick.label1.set_visible(False)

        for ii, tick in enumerate(ax.xaxis.get_major_ticks()):
            tick.label.set_fontsize(ticksize)
            if (ii+tickoffsetx) % tickseparationx != 0:
                tick.label1.set_visible(False)

    elif projection == '3d':
        if 'xlabel' in labels.keys():
            xlabel = labels['xlabel']
            ax.set_xlabel(xlabel, fontsize=14, labelpad=15)
        if 'ylabel' in labels.keys():
            ylabel = labels['ylabel']
            ax.set_ylabel(ylabel, fontsize=14, labelpad=15)
        if 'zlabel' in labels.keys():
            zlabel = labels['zlabel']
            ax.set_zlabel(zlabel, fontsize=14, labelpad=15)

        for ii, tick in enumerate(ax.yaxis.get_major_ticks()):
            tick.label.set_fontsize(ticksize)
            if (ii+tickoffsety) % tickseparationy != 0:
                tick.label1.set_visible(False)

        for ii, tick in enumerate(ax.xaxis.get_major_ticks()):
            tick.label.set_fontsize(ticksize)
            if (ii+tickoffsetx) % tickseparationx != 0:
                tick.label1.set_visible(False)

        for ii, tick in enumerate(ax.zaxis.get_major_ticks()):
            tick.label.set_fontsize(ticksize)
            if ii % 2 != 0:
                tick.label1.set_visible(False)

        ax.view_init(20,-120)


    return ax
