import numpy as np
import scipy.stats as stats

# from IPython.core.display import display, HTML


def display_dict(m, precision=3):
    table = "<table>"
    for item in m.items():
        table += ("<tr><th>{0}</th><td>{1:." + str(precision) + "f}</td></tr>").format(*item)
    table += "</table>"
    return display(HTML(table))


def calculate_tukey_five(data):
    min, q1, q2, q3, max = np.concatenate([[np.min(data)], stats.mstats.mquantiles( data, [0.25, 0.5, 0.75]),[np.max(data)]])
    data = {"Min": min, "Q1": q1, "Q2": q2, "Q3": q3, "Max": max}
    return data


def calculate_tukey_dispersion(five):
    data = {
        "Range": five["Max"] - five["Min"],
        "IQR": five["Q3"] - five["Q1"],
        "QCV": (five["Q3"] - five["Q1"]) / five["Q2"]
    }
    return data


def restyle_boxplot(patch):
    ## change color and linewidth of the whiskers
    for whisker in patch['whiskers']:
        whisker.set(color='#000000', linewidth=1)

    ## change color and linewidth of the caps
    for cap in patch['caps']:
        cap.set(color='#000000', linewidth=1)

    ## change color and linewidth of the medians
    for median in patch['medians']:
        median.set(color='#000000', linewidth=2)

    ## change the style of fliers and their fill
    for flier in patch['fliers']:
        flier.set(marker='o', color='#000000', alpha=0.2)

    for box in patch["boxes"]:
        box.set( facecolor='#FFFFFF', alpha=0.5)
