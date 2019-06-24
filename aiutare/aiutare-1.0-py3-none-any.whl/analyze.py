#!/usr/bin/env python3
import time
import importlib
import numpy as np
import matplotlib.pyplot as plt
from bin.config import config


# PLOTTING HELPERS

def scatter_plot(ax, x_data, y_data, label):
    # Plot the data, set the size (s), color and transparency (alpha) of the points
    ax.scatter(x_data, y_data, s=10, alpha=0.75, label=label)


def grouped_bar_plot(ax, x_data, y_data_list, y_data_names):
    # Total width for all bars at one x location
    total_width = 0.8
    # Width of each individual bar
    ind_width = total_width / len(y_data_list)
    # This centers each cluster of bars about the x tick mark
    alteration = np.arange(-(total_width / 2), total_width / 2, ind_width)

    # Draw bars, one category at a time
    for i in range(0, len(y_data_list)):
        # Move the bar to the right on the x-axis so it doesn't
        # overlap with previously drawn ones
        ax.bar(x_data + alteration[i], y_data_list[i], label=y_data_names[i], width=ind_width)


# PLOTTING FUNCTIONS

def plot_cactus(data, name, show_date=False, yscale_log=True, out_type="pdf"):
    x_label = "Instance #"
    y_label = "Time (s)"
    title = "Cactus: %s" % " vs. ".join(solver for solver in data.keys())

    if show_date:
        title += " (%s)" % time.strftime("%d/%m/%Y")

    # Create the plot object
    fig, ax = plt.subplots()

    if yscale_log:
        ax.set_yscale('log')

    # Label the axes and provide a title
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    for solver, runs in data.items():
        flt = [r[-1] for r in runs if r[1] in ['sat', 'unsat']]
        scatter_plot(ax, list(range(len(flt))), sorted(flt), solver)

    ax.legend()
    fig.savefig("%s/%s" % ("images/", "%s.%s" % (name, out_type)), bbox_inches='tight')
    plt.close(fig)


def plot_times(data, name, average=True, include_overall=False, show_date=False, out_type="pdf"):
    y_label = "Average Time (s)" if average else "Time (s)"
    title = "Times: %s" % " vs. ".join(solver for solver in data.keys())

    if show_date:
        title += " (%s)" % time.strftime("%d/%m/%Y")

    # Create the plot object
    fig, ax = plt.subplots()

    # Label the axes and provide a title
    ax.set_title(title)
    ax.set_ylabel(y_label)

    choices = ["sat", "unsat", "unknown", "error", "overall"]
    choices = choices if include_overall else choices[:-1]
    x_data = list(range(len(choices)))
    y_data_list = []
    solvers = []

    for solver, runs in data.items():
        solvers.append(solver)
        times = time_results(runs)

        if average:
            count = count_results(runs)
            count = [count[0], count[1], count[2], count[4]]  # remove timeouts
            count = count + [sum(count)] if include_overall else count

            for i in range(len(count)):
                times[i] = times[i] / count[i] if count[i] > 0 else 0

        y_data_list.append(times if include_overall else times[:-1])

    grouped_bar_plot(ax, x_data, y_data_list, solvers)
    ax.set_xticklabels(choices)
    ax.set_xticks(list(range(len(choices))))
    ax.legend()
    fig.savefig("%s/%s" % ("images/", "%s.%s" % (name, out_type)), bbox_inches='tight')
    plt.close(fig)

    print_times(average, choices, solvers, y_data_list)


def plot_counts(data, name, show_date=False, out_type="pdf"):
    y_label = "# Occurences"
    title = "Counts: %s" % " vs. ".join(solver for solver in data.keys())

    if show_date:
        title += " (%s)" % time.strftime("%d/%m/%Y")

    # Create the plot object
    fig, ax = plt.subplots()

    # Label the axes and provide a title
    ax.set_title(title)
    ax.set_ylabel(y_label)

    choices = ["sat", "unsat", "unknown", "timeout", "error"]
    x_data = list(range(len(choices)))
    counts = []
    solvers = []

    for solver, runs in data.items():
        solvers.append(solver)
        counts.append(count_results(runs))

    grouped_bar_plot(ax, x_data, counts, solvers)
    ax.set_xticklabels(choices)
    ax.set_xticks(list(range(len(choices))))
    ax.legend()
    fig.savefig("%s/%s" % ("images/", "%s.%s" % (name, out_type)), bbox_inches='tight')
    plt.close(fig)

    print_counts(choices, solvers, counts)


# ANALYSIS AND AGGREGATION

def count_results(runs):
    choices = ["sat", "unsat", "unknown", "timeout", "error"]
    results = [0 for _ in choices]

    for r in runs["Result"]:
        if r == "sat":
            results[0] += 1
        if r == "unsat":
            results[1] += 1
        if r == "unknown":
            results[2] += 1
        if "timeout" in r:
            results[3] += 1
        if r == "error":
            results[4] += 1

    return results


def time_results(runs):
    choices = ["sat", "unsat", "unknown", "error", "overall"]
    results = [0 for _ in choices]

    for r in range(len(runs["Result"])):
        if runs["Result"][r] == "sat":
            results[0] += runs["Time"][r]
        if runs["Result"][r] == "unsat":
            results[1] += runs["Time"][r]
        if runs["Result"][r] == "unknown":
            results[2] += runs["Time"][r]
        if runs["Result"][r] == "error":
            results[3] += runs["Time"][r]
        results[4] += runs["Time"][r]

    return results


def check_consensus(data):
    # ASSUMING IN SAME ORDER!!!
    issues = []
    min_solved = min(len(runs) for solver, runs in data.items())

    for i in range(min_solved):
        votes = {}

        for solver, runs in data.items():
            votes[solver] = runs["Result"][i]
            problem = runs['Instance'][i]

        done = False
        for _, va in votes.items():
            if done:
                break
            for _, vb in votes.items():
                if done:
                    break
                if va != vb and va in ['sat', 'unsat'] and vb in ['sat', 'unsat']:
                    issues.append((problem, votes))
                    done = True
                    break

    print_consensus_issues(issues)


# PRINTING RESULTS

def print_consensus_issues(issues):
    if len(issues) == 0:
        return

    print("\nDisagreements (%d):" % len(issues))
    print("Instance,", ", ".join(solver for solver in issues[0][1].keys()))

    for i in issues:
        print("%s," % i[0], ", ".join(i[1][solver] for solver in i[1].keys()))


def print_counts(choices, solvers, counts):
    print("\nCounts:")
    print("solver,", ", ".join(c for c in choices))

    for i in range(len(counts)):
        print(", ".join(c for c in [solvers[i]] + list(map(str, counts[i]))))


def print_times(average, choices, solvers, times):
    print("\nAverage Times (s):") if average else print("\nTimes (s):")
    print("solver,", ", ".join(c for c in choices))

    for i in range(len(times)):
        print(", ".join(c for c in [solvers[i]] + list(map(repr, times[i]))))


def import_category():
    schemas = importlib.import_module(config["schemas"])
    return schemas.read_database()


# ENTRY POINT

def analyze():
    data = import_category()

    check_consensus(data)
    plot_cactus(data, "overall_cactus")
    plot_counts(data, "overall_counts")
    plot_times(data, "overall_times")
