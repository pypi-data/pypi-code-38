"""
Author: Rohit Suratekar

These are functions used in generating plots on https://weirddata.github.io/
Blog Post: Matplotlib vs SecretColors
"""

import matplotlib
import matplotlib.pylab as plt
import numpy as np
import seaborn as sns

from SecretColors.palette import Palette, ColorMap


def bar_plots():
    p = Palette()
    data = np.random.random(6)
    mat_colors = ["r", "b", "g", "y", "m", "c"]
    ibm_colors = [p.red(), p.blue(), p.green(), p.yellow(), p.magenta(),
                  p.cyan()]

    plt.subplot(121)

    for i, v in enumerate(data):
        plt.bar(i, v, color=mat_colors[i])
        plt.xticks([])
        plt.yticks([])
        plt.title("Matplotlib")

    plt.subplot(122)
    for i, v in enumerate(data):
        plt.bar(i, v, color=ibm_colors[i])
        plt.xticks([])
        plt.yticks([])
        plt.title("SecretColors")

    plt.show()


def bar_plot_color_cycle():
    p = Palette()
    data = np.random.random(10)

    plt.subplot(121)

    for i, v in enumerate(data):
        plt.bar(i, v)
        plt.xticks([])
        plt.yticks([])
        plt.title("Matplotlib")

    colors = p.get_color_list
    plt.subplot(122)
    for i, v in enumerate(data):
        plt.bar(i, v, color=colors[i])
        plt.xticks([])
        plt.yticks([])
        plt.title("SecretColors")

    plt.show()


def all_default_colors():
    p = Palette()
    colors = p.get_color_list

    for i, v in enumerate(colors):
        plt.bar(i, np.random.random(), color=v)
        plt.xticks([])
        plt.yticks([])
        plt.title("IBM Full Color Cycle")

    plt.show()


def test_gradient():
    ibm = Palette()
    x_data = range(0, 100, 10)
    ind = range(len(x_data))
    plt.figure(figsize=(9, 6))

    cmap = matplotlib.cm.get_cmap('Greys')
    plt.subplot(121)
    colors = [cmap(x / max(x_data)) for x in x_data]
    plt.bar(ind, x_data, color=colors)
    plt.xticks([])
    plt.yticks([])
    plt.title("Default")

    plt.subplot(122)
    new_colors = [ibm.gray(shade=int(x)) for x in x_data]
    plt.bar(ind, x_data, color=new_colors)
    plt.xticks([])
    plt.yticks([])
    plt.title("SecretColors")

    plt.show()


def test_lines():
    ibm = Palette()
    all_data = []
    for d in range(4):
        data = np.random.random(30) + d * 0.8
        all_data.append(data)
    time = range(len(all_data[0]))
    plt.figure(figsize=(9, 6))

    plt.subplot(121)
    colors = ["r", "g", "b", "y"]
    i = 0
    for data in all_data:
        plt.plot(time, data, linewidth=4, color=colors[i])
        i += 1
    plt.title("Default")

    plt.subplot(122)
    new_colors = [ibm.red(), ibm.green(), ibm.blue(), ibm.yellow()]
    i = 0
    for data in all_data:
        plt.plot(time, data, linewidth=4, color=new_colors[i])
        i += 1
    plt.title("SecretColors")

    plt.show()


def histograms():
    ibm = Palette()
    mu, sigma = 100, 15
    mu2, sigma2 = 150, 20
    x = mu + sigma * np.random.randn(10000)
    y = mu2 + sigma2 * np.random.randn(10000)

    plt.subplot(131)
    plt.hist(x, 30, color="m")
    plt.hist(y, 30, color="c")
    plt.yticks([])
    plt.xticks([])
    plt.title("Matplotlib")

    plt.subplot(132)
    plt.hist(x, 30, color=ibm.magenta())
    plt.hist(y, 30, color=ibm.cyan())
    plt.yticks([])
    plt.xticks([])
    plt.title("SecretColors Defaults")

    plt.subplot(133)
    plt.hist(x, 30, color=ibm.magenta(shade=60))
    plt.hist(y, 30, color=ibm.cyan(shade=40))
    plt.yticks([])
    plt.xticks([])
    plt.title("SecretColors Modified")

    plt.show()


def histograms_shades():
    ibm = Palette()
    mu, sigma = 100, 15
    mu2, sigma2 = 150, 20
    x = mu + sigma * np.random.randn(10000)
    y = mu2 + sigma2 * np.random.randn(10000)

    plt.subplot(131)
    plt.hist(x, 30, color=ibm.magenta(shade=30))
    plt.hist(y, 30, color=ibm.cyan())
    plt.yticks([])
    plt.xticks([])
    plt.title("shade=30")

    plt.subplot(132)
    plt.hist(x, 30, color=ibm.magenta(shade=60))
    plt.hist(y, 30, color=ibm.cyan())
    plt.yticks([])
    plt.xticks([])
    plt.title("shade=60")

    plt.subplot(133)
    plt.hist(x, 30, color=ibm.magenta(shade=80))
    plt.hist(y, 30, color=ibm.cyan())
    plt.yticks([])
    plt.xticks([])
    plt.title("shade=80")

    plt.show()


def heatmap_standard():
    ibm = Palette()
    cmap = ColorMap(matplotlib, ibm)
    a = np.random.random((16, 16))

    plt.subplot(121)
    plt.imshow(a, cmap='Greens', interpolation='nearest')
    plt.colorbar()
    plt.title("Matplotlib")

    plt.subplot(122)
    plt.imshow(a, cmap=cmap.greens(), interpolation='nearest')
    plt.colorbar()
    plt.title("SecretColors")

    plt.show()


def heatmap_custom():
    ibm = Palette(show_warning=False)
    cmap = ColorMap(matplotlib, ibm)
    a = np.random.random((16, 16))

    plt.subplot(121)
    colors = [ibm.green(shade=0), ibm.green(shade=50)]
    plt.imshow(a, cmap=cmap.from_list(colors), interpolation='nearest')
    plt.colorbar()
    plt.title("Lighter Shades")

    plt.subplot(122)
    colors = [ibm.green(shade=50), ibm.green(shade=100)]
    plt.imshow(a, cmap=cmap.from_list(colors), interpolation='nearest')
    plt.colorbar()
    plt.title("Darker Shades")

    plt.show()


def shift_colormap():
    ibm = Palette(show_warning=False)
    cmap = ColorMap(matplotlib, ibm)
    a = np.random.random((16, 16))

    plt.subplot(131)
    colors = [ibm.green(shade=0), ibm.green(shade=30), ibm.green(shade=100)]
    plt.imshow(a, cmap=cmap.from_list(colors), interpolation='nearest')
    plt.colorbar()
    plt.title("Shades : 0-30-100")

    plt.subplot(132)
    colors = [ibm.green(shade=0), ibm.green(shade=50), ibm.green(shade=100)]
    plt.imshow(a, cmap=cmap.from_list(colors), interpolation='nearest')
    plt.colorbar()
    plt.title("Shades : 0-50-100")

    plt.subplot(133)
    colors = [ibm.green(shade=0), ibm.green(shade=70), ibm.green(shade=100)]
    plt.imshow(a, cmap=cmap.from_list(colors), interpolation='nearest')
    plt.colorbar()
    plt.title("Shades : 0-70-100")

    plt.show()


def heatmap_custom2():
    ibm = Palette(show_warning=False)
    cmap = ColorMap(matplotlib, ibm)
    a = np.random.random((16, 16))

    plt.subplot(121)
    colors = [ibm.purple(shade=80), ibm.purple(shade=40), ibm.yellow(
        shade=30), ibm.yellow(shade=50)]
    plt.imshow(a, cmap=cmap.from_list(colors), interpolation='nearest')
    plt.colorbar()
    plt.title("Yellow-Purple")

    plt.subplot(122)
    colors = [ibm.lime(shade=30), ibm.brown(), ibm.black()]
    plt.imshow(a, cmap=cmap.from_list(colors), interpolation='nearest')
    plt.colorbar()
    plt.title("Black-Brown-Lime")

    plt.show()


def heatmap_qualitative():
    ibm = Palette(show_warning=False)
    cmap = ColorMap(matplotlib, ibm)
    a = np.random.random((16, 16))

    plt.subplot(121)
    colors = [ibm.green(30), ibm.green(80)]
    plt.imshow(a, cmap=cmap.from_list(colors, is_qualitative=True),
               interpolation='nearest')
    plt.colorbar()
    plt.title("Two colors")

    plt.subplot(122)
    colors = ibm.green(no_of_colors=5)
    plt.imshow(a, cmap=cmap.from_list(colors, is_qualitative=True),
               interpolation='nearest')
    plt.colorbar()
    plt.title("Five colors")

    plt.show()


def testing_seaborn():
    p = Palette()
    ind = [str(x) for x in range(10)]
    data = np.random.random(10)
    colors = {str(p.get_color_list.index(v)): v for v in p.get_color_list[:10]}
    plt.subplot(121)
    sns.barplot(x=ind, y=data)
    plt.title("Seaborn Default")
    plt.xticks([])
    plt.yticks([])
    plt.subplot(122)
    sns.barplot(x=ind, y=data, palette=colors)
    plt.title("SecretColors Default")
    plt.xticks([])
    plt.yticks([])
    plt.show()


p = Palette("clarity")
cols = [p.red(), p.blue(), p.green(), p.yellow(), p.magenta(), p.cyan()]

for i, d in enumerate(cols):
    plt.bar(i, 1, color=d)

plt.show()
