"""
Enable picking on the legend to toggle the legended line on and off
"""
import numpy as np
import matplotlib.pyplot as plt

import pylustrator
pylustrator.start()
#plt.ion()

#StartDragger()

t = np.arange(0.0, 0.2, 0.1)
y1 = 2*np.sin(2*np.pi*t)
y2 = 4*np.sin(2*np.pi*2*t)
fig = plt.figure(0, (18/2.54, 15/2.54))
"""
#fig, ax = plt.subplots()
plt.subplot(231)
line1, = plt.plot(t, y1, lw=2, color='red', label='1 HZ')

line2, = plt.plot(t, y2, lw=2, color='blue', label='2 HZ')
#leg = ax.legend(loc='upper left', fancybox=True, shadow=True)
#leg.get_frame().set_alpha(0.4)
"""
ax0 = plt.subplot(231, label="a")
#line1, = plt.plot(t, y1, lw=2, color='red', label='1 HZ')
#line2, = plt.plot(t, y2, lw=2, color='blue', label='2 HZ')

import matplotlib as mpl
p = mpl.patches.FancyArrowPatch((0.4, 0.2), (3.6, 3.3), arrowstyle="Simple,head_length=10,head_width=10,tail_width=2", shrinkA=0, shrinkB=0, facecolor="black", clip_on=False, zorder=2)
#p = mpl.patches.FancyArrowPatch((0.4, 0.2), (4.6, 4.3), arrowstyle="Simple,head_length=28,head_width=36,tail_width=20")
plt.gca().add_patch(p)
p.set_picker(True)
ax0.set_xlim(0, 5)
ax0.set_ylim(0, 5)

ax0 = plt.subplot(233, label="b")
line1, = plt.plot(t, y1, lw=2, color='red', label='1 HZ')
line2, = plt.plot(t, y2, lw=2, color='blue', label='2 HZ')
plt.xlim(-10, 10)
plt.ylim(-10, 10)
plt.legend()

ax2 = plt.subplot(235, label="c")
a = np.arange(1000).reshape(20, 50)
plt.imshow(a)

ax1 = plt.axes([0.2, 0.2, 0.2, 0.2])#subplot(234)
line1, = plt.plot(t, y1, lw=2, color='red', label='1 HZ')
line2, = plt.plot(t, y2, lw=2, color='blue', label='2 HZ')
plt.axis("equal")
plt.legend()


from mpl_toolkits.axes_grid1.inset_locator import mark_inset
mark_inset(ax0, ax1, loc1=2, loc2=4, fc="none", lw=2, ec='r')

ax3 = plt.colorbar()

plt.axis()


plt.text(0, 0, "Heyhho", transform=ax2.transAxes, picker=True)
plt.text(10, 10, "Heyhho", transform=ax2.transData, picker=True)

plt.savefig("test.png")
#% start: automatic generated code from pylustrator
fig = plt.figure(0)
import matplotlib as mpl
fig.ax_dict = {ax.get_label(): ax for ax in fig.axes}
fig.ax_dict["b"].get_legend()._set_loc((0.510049, 0.980630))
fig.axes[3].lines[0].set_color("#ff54e3ff")
fig.set_size_inches(16.780000/2.54, 14.990000/2.54, forward=True)
fig.ax_dict["a"].set_position([0.084680, 0.501225, 0.245708, 0.379191])
fig.ax_dict["a"].spines['right'].set_visible(False)
fig.ax_dict["a"].spines['top'].set_visible(False)
fig.ax_dict["a"].set_xticklabels(["0", "X", "y", "2"])
fig.ax_dict["a"].patches[0].set_positions((0.40000000000000036, 1.765325249958157), (3.600000000000007, 3.3000000000000034))
fig.ax_dict["a"].patches[0].set_edgecolor("#52219cff")
fig.ax_dict["a"].text(0.5, 0.5, 'New Text', transform=fig.ax_dict["a"].transAxes)  # id=fig.ax_dict["a"].texts[0].new
fig.ax_dict["a"].texts[0].set_text("a")
fig.ax_dict["a"].texts[0].set_position([-0.194004, 1.047215])
fig.ax_dict["b"].set_position([0.428281, 0.531628, 0.226007, 0.348788])
fig.ax_dict["b"].set_xlim(-1.0, 2.0)
fig.ax_dict["b"].text(0.5, 0.5, 'New Text', transform=fig.ax_dict["b"].transAxes)  # id=fig.ax_dict["b"].texts[0].new
fig.ax_dict["b"].texts[0].set_text("b")
fig.ax_dict["b"].texts[0].set_position([-0.243576, 1.047215])
fig.ax_dict["b"].texts[0].set_color("#2816afff")
fig.ax_dict["b"].texts[0].set_fontsize(19)
fig.ax_dict["c"].set_position([0.395190, 0.238668, 0.328156, 0.146937])
fig.axes[3].set_position([0.746627, 0.531628, 0.226007, 0.348788])
fig.axes[3].set_xlabel("asd")
fig.axes[3].set_ylabel("yyy")
fig.axes[3].xaxis.labelpad = 2.480000
fig.axes[3].set_xlim(0.0, 1.0)
fig.axes[4].set_position([0.366861, 0.203827, 0.008808, 0.197194])
#% end: automatic generated code from pylustrator
plt.show()
#plt.show()