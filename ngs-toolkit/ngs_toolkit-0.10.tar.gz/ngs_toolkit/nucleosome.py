import pickle
import re
from scipy.stats import mannwhitneyu
from statsmodels.sandbox.stats.multicomp import multipletests


def nucleosome_changes(analysis, samples):
    # select only ATAC-seq samples
    df = analysis.prj.sheet.df[analysis.prj.sheet.df["library"] == "ATAC-seq"]

    groups = list()
    for attrs, _ in df.groupby(
        ["library", "cell_line", "knockout", "clone"]
    ).groups.items():
        name = "_".join([a for a in attrs if not pd.isnull(a)])
        groups.append(name)
    groups = sorted(groups)

    # nucleosomes per sample
    nucpos_metrics = {
        "z-score": 4,
        "nucleosome_occupancy_estimate": 5,
        "lower_bound_for_nucleosome_occupancy_estimate": 6,
        "upper_bound_for_nucleosome_occupancy_estimat": 7,
        "log_likelihood_ratio": 8,
        "normalized_nucleoatac_signal": 9,
        "cross-correlation_signal_value_before_normalization": 10,
        "number_of_potentially_nucleosome-sized_fragments": 11,
        "number_of_fragments_smaller_than_nucleosome_sized": 12,
        "fuzziness": 13,
    }
    # nucleosome-free regions per sample
    nfrpos_metrics = {
        "mean_occupancy": 4,
        "minimum_upper_bound_occupancy": 5,
        "insertion_density": 6,
        "bias_density": 7,
    }
    for data_type, metrics in [("nucpos", nucpos_metrics), ("nfrpos", nfrpos_metrics)]:
        figs = list()
        axizes = list()
        for metric in metrics:
            fig, axis = plt.subplots(
                5, 6, figsize=(6 * 4, 5 * 4), sharex=True, sharey=True
            )
            figs.append(fig)
            axizes.append(axis.flatten())

        counts = pd.Series()
        for i, group in enumerate(groups):
            _LOGGER.info("{}, {}".format(data_type, group))
            s = pd.read_csv(
                os.path.join(
                    "results",
                    "nucleoatac",
                    group,
                    group + ".{}.bed.gz".format(data_type),
                ),
                sep="\t",
                header=None,
            )
            counts[group] = s.shape[0]

            for j, (metric, col) in enumerate(metrics.items()):
                _LOGGER.info(data_type, group, metric, col)
                sns.distplot(s[col - 1].dropna(), hist=False, ax=axizes[j][i])
                axizes[j][i].set_title(group)

        for i, metric in enumerate(metrics):
            sns.despine(figs[i])
            figs[i].savefig(
                os.path.join(
                    "results",
                    "nucleoatac",
                    "plots",
                    "{}.{}.svg".format(data_type, metric),
                ),
                bbox_inches="tight",
            )

        fig, axis = plt.subplots(1, 1, figsize=(1 * 4, 1 * 4))
        sns.barplot(
            counts,
            counts.index,
            orient="horizontal",
            ax=axis,
            color=sns.color_palette("colorblind")[0],
        )
        axis.set_yticklabels(axis.get_yticklabels(), rotation=0)
        axis.set_xlabel("Calls")
        sns.despine(fig)
        fig.savefig(
            os.path.join(
                "results",
                "nucleoatac",
                "plots",
                "{}.count_per_sample.svg".format(data_type),
            ),
            bbox_inches="tight",
        )

    # fragment distribution
    for data_type in ["InsertionProfile", "InsertSizes", "fragmentsizes"]:
        fig, axis = plt.subplots(5, 6, figsize=(6 * 4, 5 * 4))
        axis = axis.flatten()

        data = pd.DataFrame()
        for i, group in enumerate(groups):
            _LOGGER.info("{}, {}".format(data_type, group))
            s = pd.read_csv(
                os.path.join(
                    "results", "nucleoatac", group, group + ".{}.txt".format(data_type)
                ),
                sep="\t",
                header=None,
                squeeze=True,
                skiprows=5 if data_type == "fragmentsizes" else 0,
            )
            if data_type == "InsertionProfile":
                a = (len(s.index) - 1) / 2.0
                s.index = np.arange(-a, a + 1)
            if data_type == "fragmentsizes":
                s = s.squeeze()
            data[group] = s

            axis[i].plot(s)
            axis[i].set_title(group)
        sns.despine(fig)
        fig.savefig(
            os.path.join("results", "nucleoatac", "plots", "{}.svg".format(data_type)),
            bbox_inches="tight",
        )

        norm_data = data.apply(lambda x: x / data["ATAC-seq_HAP1_WT_C631"])
        if data_type == "fragmentsizes":
            norm_data = norm_data.loc[50:, :]
        fig, axis = plt.subplots(5, 6, figsize=(6 * 4, 5 * 4), sharey=True)
        axis = axis.flatten()
        for i, group in enumerate(groups):
            _LOGGER.info("{}, {}".format(data_type, group))
            axis[i].plot(norm_data[group])
            axis[i].set_title(group)
        sns.despine(fig)
        fig.savefig(
            os.path.join(
                "results", "nucleoatac", "plots", "{}.WT_norm.svg".format(data_type)
            ),
            bbox_inches="tight",
        )

    # Vplots and
    v_min, v_max = (105, 251)
    # Vplots over WT
    for data_type in ["VMat"]:
        fig, axis = plt.subplots(5, 6, figsize=(6 * 4, 5 * 4))
        fig2, axis2 = plt.subplots(5, 6, figsize=(6 * 4, 5 * 4), sharey=True)
        axis = axis.flatten()
        axis2 = axis2.flatten()

        group = "ATAC-seq_HAP1_WT_C631"
        wt = pd.read_csv(
            os.path.join(
                "results", "nucleoatac", group, group + ".{}".format(data_type)
            ),
            sep="\t",
            header=None,
            skiprows=7,
        )
        wt.index = np.arange(v_min, v_max)
        a = (len(wt.columns) - 1) / 2.0
        wt.columns = np.arange(-a, a + 1)
        wt = wt.loc[0:300, :]

        for i, group in enumerate(groups):
            _LOGGER.info("{}, {}".format(data_type, group))
            m = pd.read_csv(
                os.path.join(
                    "results", "nucleoatac", group, group + ".{}".format(data_type)
                ),
                sep="\t",
                header=None,
                skiprows=7,
            )
            m.index = np.arange(v_min, v_max)
            a = (len(m.columns) - 1) / 2.0
            m.columns = np.arange(-a, a + 1)
            m = m.loc[0:300, :]

            n = m / wt

            axis[i].imshow(m.sort_index(ascending=False))
            axis[i].set_title(group)
            axis2[i].imshow(n.sort_index(ascending=False))
            axis2[i].set_title(group)
        sns.despine(fig)
        sns.despine(fig2)
        fig.savefig(
            os.path.join("results", "nucleoatac", "plots", "{}.svg".format(data_type)),
            bbox_inches="tight",
        )
        fig2.savefig(
            os.path.join(
                "results", "nucleoatac", "plots", "{}.WT_norm.svg".format(data_type)
            ),
            bbox_inches="tight",
        )


def investigate_nucleosome_positions(self, samples, cluster=True):
    df = self.prj.sheet.df[self.prj.sheet.df["library"] == "ATAC-seq"]
    groups = list()
    for attrs, index in df.groupby(
        ["library", "cell_line", "knockout", "clone"]
    ).groups.items():
        name = "_".join([a for a in attrs if not pd.isnull(a)])
        groups.append(name)
    groups = sorted(groups)

    def get_differential(diff, conditions_for, directions_for):
        # filter conditions
        d = diff[diff["comparison"].isin(conditions_for)]

        # filter directions
        d = pd.concat([d[f(d["log2FoldChange"], x)] for f, x in directions_for])

        # make bed format
        df = (
            pd.Series(d.index.str.split(":"))
            .apply(lambda x: pd.Series([x[0]] + x[1].split("-")))
            .drop_duplicates()
            .reset_index(drop=True)
        )
        df[0] = df[0].astype(str)
        df[1] = df[1].astype(np.int64)
        df[2] = df[2].astype(np.int64)
        return df

    def center_window(bedtool, width=1000):
        chroms = ["chr" + str(x) for x in range(1, 23)] + ["chrX", "chrY"]

        sites = list()
        for site in bedtool:
            if site.chrom in chroms:
                mid = site.start + ((site.end - site.start) / 2)
                sites.append(
                    pybedtools.Interval(
                        site.chrom, mid - (width / 2), (mid + 1) + (width / 2)
                    )
                )
        return pybedtools.BedTool(sites)

    def center_series(series, width=1000):
        mid = series[1] + ((series[2] - series[1]) / 2)
        return pd.Series([series[0], mid - (width / 2), (mid + 1) + (width / 2)])

    # Regions to look at
    regions_pickle = os.path.join(
        self.results_dir, "nucleoatac", "all_types_of_regions.pickle"
    )
    if os.path.exists(regions_pickle):
        regions = pickle.load(open(regions_pickle, "rb"))
    else:
        regions = dict()
        # All accessible sites
        out = os.path.join(self.results_dir, "nucleoatac", "all_sites.bed")
        center_window(self.sites).to_dataframe()[["chrom", "start", "end"]].to_csv(
            out, index=False, header=None, sep="\t"
        )
        regions["all_sites"] = out

        # get bed file of promoter proximal sites
        promoter_sites = os.path.join(
            self.results_dir, "nucleoatac", "promoter_proximal.bed"
        )
        self.coverage_annotated[self.coverage_annotated["distance"].astype(int) < 5000][
            ["chrom", "start", "end"]
        ].to_csv(promoter_sites, index=False, header=None, sep="\t")
        regions["promoter"] = promoter_sites

        # All accessible sites - that are distal
        out = os.path.join(self.results_dir, "nucleoatac", "distal_sites.bed")
        (
            center_window(
                self.sites.intersect(
                    pybedtools.BedTool(promoter_sites), v=True, wa=True
                )
            )
            .to_dataframe()[["chrom", "start", "end"]]
            .to_csv(out, index=False, header=None, sep="\t")
        )
        regions["distal_sites"] = out

        # Differential sites
        diff = pd.read_csv(
            os.path.join("results", "deseq_knockout", "deseq_knockout.knockout.csv"),
            index_col=0,
        )
        diff = diff[(diff["padj"] < 0.01) & (abs(diff["log2FoldChange"]) > 1.0)]

        # Loosing accessibility with ARID1A/SMARCA4 KO
        less_ARID1ASMARCA4 = get_differential(
            diff,
            ["ARID1A-WT", "SMARCA4-WT"],
            [(np.less_equal, -1), (np.less_equal, -1)],
        ).apply(center_series, axis=1)
        out = os.path.join(
            self.results_dir, "nucleoatac", "diff_sites.less_ARID1ASMARCA4.bed"
        )
        less_ARID1ASMARCA4.to_csv(out, index=False, header=None, sep="\t")
        regions["diff_sites.less_ARID1ASMARCA4"] = out

        # Gaining accessibility with ARID1A/SMARCA4 KO
        more_ARID1ASMARCA4 = get_differential(
            diff,
            ["ARID1A-WT", "SMARCA4-WT"],
            [(np.greater_equal, 1), (np.greater_equal, 1)],
        ).apply(center_series, axis=1)
        out = os.path.join(
            self.results_dir, "nucleoatac", "diff_sites.more_ARID1ASMARCA4.bed"
        )
        more_ARID1ASMARCA4.to_csv(out, index=False, header=None, sep="\t")
        regions["diff_sites.more_ARID1ASMARCA4"] = out

        # TFBSs
        tfs = ["CTCF", "BCL", "SMARC", "POU5F1", "SOX2", "NANOG", "TEAD4"]
        for tf in tfs:
            tf_bed = pybedtools.BedTool(
                "/home/arendeiro/resources/genomes/hg19/motifs/TFs/{}.true.bed".format(
                    tf
                )
            )
            out = os.path.join(self.results_dir, "nucleoatac", "tfbs.%s.bed" % tf)
            center_window(tf_bed.intersect(self.sites, wa=True)).to_dataframe()[
                ["chrom", "start", "end"]
            ].to_csv(out, index=False, header=None, sep="\t")
            regions["tfbs.%s" % tf] = out

        pickle.dump(regions, open(regions_pickle, "wb"))

    # Launch jobs
    for group in groups:
        output_dir = os.path.join(self.results_dir, "nucleoatac", group)

        # Signals to measure in regions
        signal_files = [
            (
                "signal",
                os.path.join(self.data_dir, "merged", group + ".merged.sorted.bam"),
            ),
            (
                "nucleosome",
                os.path.join(self.data_dir, "merged", group + ".nucleosome_reads.bam"),
            ),
            (
                "nucleosome_free",
                os.path.join(
                    self.data_dir, "merged", group + ".nucleosome_free_reads.bam"
                ),
            ),
            (
                "nucleoatac",
                os.path.join(
                    "results",
                    "nucleoatac",
                    group,
                    group + ".nucleoatac_signal.smooth.bedgraph.gz",
                ),
            ),
            (
                "dyads",
                os.path.join("results", "nucleoatac", group, group + ".nucpos.bed.gz"),
            ),
        ]
        for region_name, bed_file in regions.items():
            for label, signal_file in signal_files:
                _LOGGER.info(group, region_name, label)
                # run job
                run_coverage_job(
                    bed_file,
                    signal_file,
                    label,
                    ".".join([group, region_name, label]),
                    output_dir,
                    window_size=2001,
                )
                # run vplot
                if label == "signal":
                    run_vplot_job(
                        bed_file,
                        signal_file,
                        ".".join([group, region_name, label]),
                        output_dir,
                    )

    # Collect signals
    signals = pd.DataFrame(columns=["group", "region", "label"])
    # signals = pd.read_csv(os.path.join(self.results_dir, "nucleoatac", "collected_coverage.csv"))

    for group in [
        g
        for g in groups
        if any(
            [re.match(".*%s.*" % x, g) for x in ["C631", "HAP1_ARID1", "HAP1_SMARCA"]]
        )
    ]:
        output_dir = os.path.join(self.results_dir, "nucleoatac", group)
        signal_files = [
            # ("signal", os.path.join(self.data_dir, "merged", group + ".merged.sorted.bam")),
            # ("nucleosome", os.path.join(self.data_dir, "merged", group + ".nucleosome_reads.bam")),
            # ("nucleosome_free", os.path.join(self.data_dir, "merged", group + ".nucleosome_free_reads.bam")),
            (
                "nucleoatac",
                os.path.join(
                    "results",
                    "nucleoatac",
                    group,
                    group + ".nucleoatac_signal.smooth.bedgraph.gz",
                ),
            ),
            # ("dyads", os.path.join("results", "nucleoatac", group, group + ".nucpos.bed.gz"))
        ]
        for region_name, bed_file in [regions.items()[-1]]:
            for label, signal_file in signal_files:
                # Skip already done
                if (
                    len(
                        signals[
                            (signals["group"] == group)
                            & (signals["region"] == region_name)
                            & (signals["label"] == label)
                        ]
                    )
                    > 0
                ):
                    print("Continuing", group, region_name, label)
                    continue

                _LOGGER.info(group, region_name, label)
                df = pd.read_csv(
                    os.path.join(
                        output_dir,
                        "{}.coverage_matrix.csv".format(
                            ".".join([group, region_name, label, label])
                        ),
                    ),
                    index_col=0,
                )
                df = (
                    df.mean(0)
                    .reset_index(name="value")
                    .rename(columns={"index": "distance"})
                )
                df["group"] = group
                df["region"] = region_name
                df["label"] = label
                signals = signals.append(df, ignore_index=True)
    signals.to_csv(
        os.path.join(self.results_dir, "nucleoatac", "collected_coverage.csv"),
        index=False,
    )

    signals = pd.read_csv(
        os.path.join(self.results_dir, "nucleoatac", "collected_coverage.csv")
    )

    signals = signals[(signals["distance"] > -400) & (signals["distance"] < 400)]

    # plot together
    region_order = sorted(signals["region"].unique(), reverse=True)
    group_order = sorted(signals["group"].unique(), reverse=True)
    label_order = sorted(signals["label"].unique(), reverse=True)

    # raw
    g = sns.FacetGrid(
        signals,
        hue="group",
        col="region",
        row="label",
        hue_order=group_order,
        row_order=label_order,
        col_order=region_order,
        sharex=False,
        sharey=False,
    )
    g.map(plt.plot, "distance", "value")
    g.add_legend()
    g.savefig(
        os.path.join(
            self.results_dir,
            "nucleoatac",
            "plots",
            "collected_coverage.raw_mean_coverage.svg",
        ),
        bbox_inches="tight",
    )

    # normalized
    signals["norm_values"] = signals.groupby(["region", "label", "group"])[
        "value"
    ].apply(lambda x: (x - x.mean()) / x.std())

    g = sns.FacetGrid(
        signals,
        hue="group",
        col="region",
        row="label",
        hue_order=group_order,
        row_order=label_order,
        col_order=region_order,
        sharex=False,
        sharey=False,
    )
    g.map(plt.plot, "distance", "norm_values")
    g.add_legend()
    g.savefig(
        os.path.join(
            self.results_dir,
            "nucleoatac",
            "plots",
            "collected_coverage.norm_mean_coverage.svg",
        ),
        bbox_inches="tight",
    )

    # normalized smoothed
    signals["norm_smooth_values"] = signals.groupby(["region", "label", "group"])[
        "value"
    ].apply(lambda x: pd.rolling_window(((x - x.mean()) / x.std()), 10))

    g = sns.FacetGrid(
        signals,
        hue="group",
        col="region",
        row="label",
        hue_order=group_order,
        row_order=label_order,
        col_order=region_order,
        sharex=False,
        sharey=False,
    )
    g.map(plt.plot, "distance", "norm_smooth_values")
    g.add_legend()
    g.savefig(
        os.path.join(
            self.results_dir,
            "nucleoatac",
            "plots",
            "collected_coverage.norm_mean_coverage.smooth.svg",
        ),
        bbox_inches="tight",
    )

    #
    # specific regions/samples
    specific_signals = signals[
        (signals["group"].str.contains("ARID1|SMARCA|C631"))
        & (~signals["group"].str.contains("OV90|GFP"))
        &
        # (signals["region"].str.contains("diff_sites")) &
        (signals["label"] == "nucleoatac")
    ]

    region_order = sorted(specific_signals["region"].unique(), reverse=True)
    group_order = sorted(specific_signals["group"].unique(), reverse=True)
    label_order = sorted(specific_signals["label"].unique(), reverse=True)

    g = sns.FacetGrid(
        specific_signals,
        hue="group",
        col="region",
        col_wrap=4,
        hue_order=group_order,
        row_order=label_order,
        col_order=region_order,
        sharex=False,
        sharey=False,
    )
    g.map(plt.plot, "distance", "value")
    g.add_legend()
    g.savefig(
        os.path.join(
            self.results_dir,
            "nucleoatac",
            "plots",
            "collected_coverage.specific.extended.svg",
        ),
        bbox_inches="tight",
    )

    # normalized (centered), zoom in center
    specific_signals["norm_values"] = specific_signals.groupby(
        ["region", "label", "group"]
    )["value"].apply(lambda x: (x - x.mean()) / x.std())
    specific_signals = specific_signals[
        (specific_signals["distance"] < 200) & (specific_signals["distance"] > -200)
    ]
    g = sns.FacetGrid(
        specific_signals,
        hue="group",
        col="region",
        row="label",
        hue_order=group_order,
        row_order=label_order,
        col_order=region_order,
        sharex=False,
        sharey=False,
    )
    g.map(plt.plot, "distance", "norm_values")
    g.add_legend()
    g.savefig(
        os.path.join(
            self.results_dir,
            "nucleoatac",
            "plots",
            "collected_coverage.specific.norm.svg",
        ),
        bbox_inches="tight",
    )

    #

    # Violinplots of nucleosome occupancies

    # Heatmap of nucleosome occupancies
    # Collect signals
    sel_groups = [
        x
        for x in groups
        if "OV90" not in x
        and "GFP" not in x
        and ("ARID1" in x or "SMARCA" in x or "WT" in x)
    ]
    regions = pickle.load(open(regions_pickle, "rb"))
    sel_regions = {k: v for k, v in regions.items() if "diff" in k}

    # get parameters based on WT accessibility
    region_order = dict()
    region_vmax = dict()
    region_norm_vmax = dict()
    output_dir = os.path.join(self.results_dir, "nucleoatac", "ATAC-seq_HAP1_WT_C631")
    for region_name in sel_regions.keys():
        df = pd.read_csv(
            os.path.join(
                output_dir,
                "{}.coverage_matrix.csv".format(
                    ".".join(
                        [
                            "ATAC-seq_HAP1_WT_C631",
                            region_name,
                            "nucleoatac",
                            "nucleoatac",
                        ]
                    )
                ),
            ),
            index_col=0,
        )
        # vmax
        region_vmax[region_name] = np.percentile(df, 95)
        region_norm_vmax[region_name] = np.percentile((df - df.mean(0)) / df.std(0), 95)
        # region order
        region_order[region_name] = df.sum(axis=1).sort_values().index  # sorted by mean
        # region_order[region_name] = g.dendrogram_row.dendrogram

    # plot all
    fig, axis = plt.subplots(
        len(sel_regions),
        len(sel_groups),
        figsize=(len(sel_groups) * 4, len(sel_regions) * 4),
    )
    fig2, axis2 = plt.subplots(
        len(sel_regions),
        len(sel_groups),
        figsize=(len(sel_groups) * 4, len(sel_regions) * 4),
    )
    for j, group in enumerate(sorted(sel_groups, reverse=True)):
        output_dir = os.path.join(self.results_dir, "nucleoatac", group)
        signal_files = [
            (
                "nucleoatac",
                os.path.join(
                    "results",
                    "nucleoatac",
                    group,
                    group + ".nucleoatac_signal.smooth.bedgraph.gz",
                ),
            )
        ]
        for i, (region_name, bed_file) in enumerate(sel_regions.items()):
            for label, signal_file in signal_files:
                _LOGGER.info("{}, {}, {}".format(group, region_name, label))
                df = pd.read_csv(
                    os.path.join(
                        output_dir,
                        "{}.coverage_matrix.csv".format(
                            ".".join([group, region_name, label, label])
                        ),
                    ),
                    index_col=0,
                )

                d = df.ix[region_order[region_name]]
                axis[i, j].imshow(
                    d,
                    norm=None,
                    cmap="inferno",
                    vmax=region_vmax[region_name],
                    extent=[-500, 500, 0, 10],
                    aspect="auto",
                )  # aspect=100
                d_norm = (d - d.mean(0)) / d.std(0)
                axis2[i, j].imshow(
                    d_norm,
                    norm=None,
                    cmap="inferno",
                    vmax=region_norm_vmax[region_name],
                    extent=[-500, 500, 0, 10],
                    aspect="auto",
                )  # aspect=100
                for ax in [axis, axis2]:
                    ax[i, j].set_title(group)
                    ax[i, j].set_xlabel("distance")
                    ax[i, j].set_ylabel(region_name)
    sns.despine(fig, top=True, right=True, left=True, bottom=True)
    sns.despine(fig2, top=True, right=True, left=True, bottom=True)
    fig.savefig(
        os.path.join(
            self.results_dir,
            "nucleoatac",
            "plots",
            "collected_coverage.specific.heatmap.png",
        ),
        bbox_inches="tight",
        dpi=300,
    )
    fig.savefig(
        os.path.join(
            self.results_dir,
            "nucleoatac",
            "plots",
            "collected_coverage.specific.heatmap.svg",
        ),
        bbox_inches="tight",
    )
    fig2.savefig(
        os.path.join(
            self.results_dir,
            "nucleoatac",
            "plots",
            "collected_coverage.specific.heatmap.centered.png",
        ),
        bbox_inches="tight",
        dpi=300,
    )
    fig2.savefig(
        os.path.join(
            self.results_dir,
            "nucleoatac",
            "plots",
            "collected_coverage.specific.heatmap.centered.svg",
        ),
        bbox_inches="tight",
    )


def phasograms(
    self, samples, max_dist=10000, rolling_window=50, plotting_window=(0, 500)
):
    from ngs_toolkit.general import detect_peaks
    from scipy.ndimage.filters import gaussian_filter1d

    df = self.prj.sheet.df[self.prj.sheet.df["library"] == "ATAC-seq"]
    groups = list()
    for attrs, index in df.groupby(
        ["library", "cell_line", "knockout", "clone"]
    ).groups.items():
        name = "_".join([a for a in attrs if not pd.isnull(a)])
        groups.append(name)
    groups = sorted(groups)

    def difference_matrix(a):
        x = np.reshape(a, (len(a), 1))
        return x - x.transpose()

    distances = dict()

    for group in groups:
        _LOGGER.info(group)
        # Get dyad calls from nucleoatac
        df = pd.read_csv(
            os.path.join(
                self.results_dir, "nucleoatac", group, group + ".nucpos.bed.gz"
            ),
            sep="\t",
            header=None,
        )

        # separate by chromosome (groupby?)
        # count pairwise distance
        dists = list()
        for chrom in df[0].unique():
            d = abs(difference_matrix(df[df[0] == chrom][1]))
            dd = d[(d < max_dist) & (d != 0)]
            dists += dd.tolist()
        distances[group] = dists

    pickle.dump(
        distances,
        open(
            os.path.join(self.results_dir, "nucleoatac", "phasogram.distances.pickle"),
            "wb",
        ),
        protocol=pickle.HIGHEST_PROTOCOL,
    )
    distances = pickle.load(
        open(
            os.path.join(self.results_dir, "nucleoatac", "phasogram.distances.pickle"),
            "rb",
        )
    )

    # Plot distances between dyads
    n_rows = n_cols = int(np.ceil(np.sqrt(len(groups))))
    n_rows -= 1
    fig, axis = plt.subplots(
        n_rows, n_cols, sharex=True, sharey=True, figsize=(n_cols * 3, n_rows * 2)
    )
    fig2, axis2 = plt.subplots(
        n_rows, n_cols, sharex=True, sharey=True, figsize=(n_cols * 3, n_rows * 2)
    )
    axis = axis.flatten()
    axis2 = axis2.flatten()
    for i, group in enumerate(groups):
        # Count frequency of dyad distances
        x = pd.Series(distances[group])
        y = x.value_counts().sort_index()
        y = y.ix[range(plotting_window[0], plotting_window[1])]
        y /= y.sum()

        # Find peaks
        y2 = pd.Series(gaussian_filter1d(y, 5), index=y.index)
        peak_indices = detect_peaks(y2.values, mpd=73.5)[:3]
        _LOGGER.info("{}, {}".format(group, y2.iloc[peak_indices].index))

        # Plot distribution and peaks
        axis[i].plot(y.index, y, color="black", alpha=0.6, linewidth=0.5)
        axis[i].plot(
            y2.index, y2, color=sns.color_palette("colorblind")[0], linewidth=1
        )
        axis[i].scatter(
            y2.iloc[peak_indices].index, y2.iloc[peak_indices], s=25, color="orange"
        )
        for peak in y2.iloc[peak_indices].index:
            axis[i].axvline(peak, color="black", linestyle="--")
        axis[i].set_title(group)

        # Transform into distances between nucleosomes
        # Plot distribution and peaks
        axis2[i].plot(y.index - 147, y, color="black", alpha=0.6, linewidth=0.5)
        axis2[i].plot(
            y2.index - 147, y2, color=sns.color_palette("colorblind")[0], linewidth=1
        )
        axis2[i].scatter(
            y2.iloc[peak_indices].index - 147,
            y2.iloc[peak_indices],
            s=25,
            color="orange",
        )
        for peak in y2.iloc[peak_indices].index:
            axis2[i].axvline(peak - 147, color="black", linestyle="--")
        axis2[i].set_title(group)
    sns.despine(fig)
    sns.despine(fig2)
    fig.savefig(
        os.path.join(
            self.results_dir,
            "nucleoatac",
            "plots",
            "phasograms.dyad_distances.peaks.svg",
        ),
        bbox_inches="tight",
    )
    fig2.savefig(
        os.path.join(
            self.results_dir,
            "nucleoatac",
            "plots",
            "phasograms.nucleosome_distances.peaks.svg",
        ),
        bbox_inches="tight",
    )

    # Get NFR per knockout
    lengths = dict()

    for group in groups:
        _LOGGER.info(group)
        # Get NFR calls from nucleoatac
        df = pd.read_csv(
            os.path.join(
                self.results_dir, "nucleoatac", group, group + ".nfrpos.bed.gz"
            ),
            sep="\t",
            header=None,
        )
        # Get lengths
        lengths[group] = (df[2] - df[1]).tolist()

    pickle.dump(
        lengths,
        open(os.path.join(self.results_dir, "nucleoatac", "nfr.lengths.pickle"), "wb"),
        protocol=pickle.HIGHEST_PROTOCOL,
    )
    lengths = pickle.load(
        open(os.path.join(self.results_dir, "nucleoatac", "nfr.lengths.pickle"), "rb")
    )

    # plot NFR lengths
    n_rows = n_cols = int(np.ceil(np.sqrt(len(groups))))
    n_rows -= 1
    fig, axis = plt.subplots(
        n_rows, n_cols, sharex=True, sharey=True, figsize=(n_cols * 3, n_rows * 2)
    )
    axis = axis.flatten()
    for i, group in enumerate(groups):
        # Count NFR lengths
        x = pd.Series(lengths[group])
        y = x.value_counts().sort_index()
        y = y.ix[range(plotting_window[0], 300)]
        y /= y.sum()

        # Find peaks
        y2 = pd.Series(gaussian_filter1d(y, 5), index=y.index)
        peak_indices = [detect_peaks(y2.values, mpd=73.5)[0]]
        _LOGGER.info("{}, {}".format(group, y2.iloc[peak_indices].index))

        # Plot distribution and peaks
        axis[i].plot(y.index, y, color="black", alpha=0.6, linewidth=0.5)
        axis[i].plot(
            y2.index, y2, color=sns.color_palette("colorblind")[0], linewidth=1
        )
        axis[i].scatter(
            y2.iloc[peak_indices].index, y2.iloc[peak_indices], s=25, color="orange"
        )
        for peak in y2.iloc[peak_indices].index:
            axis[i].axvline(peak, color="black", linestyle="--")
        axis[i].set_title(group)

    sns.despine(fig)
    fig.savefig(
        os.path.join(
            self.results_dir, "nucleoatac", "plots", "phasograms.nfr_lengths.peaks.svg"
        ),
        bbox_inches="tight",
    )


def run_coverage_job(
    bed_file, bam_file, coverage_type, name, output_dir, window_size=1001
):
    from pypiper import NGSTk

    tk = NGSTk()
    job_file = os.path.join(output_dir, "%s.run_enrichment.sh" % name)
    log_file = os.path.join(output_dir, "%s.run_enrichment.log" % name)

    cmd = """#!/bin/bash
#SBATCH --partition=shortq
#SBATCH --ntasks=1
#SBATCH --time=12:00:00

#SBATCH --cpus-per-task=2
#SBATCH --mem=8000
#SBATCH --nodes=1

#SBATCH --job-name=baf-kubicek-run_enrichment_{}
#SBATCH --output={}

#SBATCH --mail-type=end
#SBATCH --mail-user=

# Start running the job
hostname
date

cd /home/arendeiro/baf-kubicek/

python /home/arendeiro/jobs/run_profiles.py \
--bed-file {} \
--bam-file {} \
--coverage-type {} \
--window-size {} \
--name {} \
--output-dir {}

date
""".format(
        name, log_file, bed_file, bam_file, coverage_type, window_size, name, output_dir
    )

    # write job to file
    with open(job_file, "w") as handle:
        handle.writelines(cmd)

    tk.slurm_submit_job(job_file)


def run_vplot_job(bed_file, bam_file, name, output_dir):
    from pypiper import NGSTk

    tk = NGSTk()
    job_file = os.path.join(output_dir, "%s.run_enrichment.sh" % name)
    log_file = os.path.join(output_dir, "%s.run_enrichment.log" % name)

    cmd = """#!/bin/bash
#SBATCH --partition=mediumq
#SBATCH --ntasks=1
#SBATCH --time=1-12:00:00

#SBATCH --cpus-per-task=8
#SBATCH --mem=24000
#SBATCH --nodes=1

#SBATCH --job-name=baf-kubicek-run_enrichment_{name}
#SBATCH --output={log}

#SBATCH --mail-type=end
#SBATCH --mail-user=

# Start running the job
hostname
date

\t\t# Remove everything to do with your python and env.  Even reset your home dir
\t\tunset PYTHONPATH
\t\tunset PYTHON_HOME
\t\tmodule purge
\t\tmodule load python/2.7.6
\t\tmodule load slurm
\t\tmodule load gcc/4.8.2

\t\tENV_DIR=/scratch/users/arendeiro/nucleoenv
\t\texport HOME=$ENV_DIR/home

\t\t# Activate your virtual env
\t\texport VIRTUALENVWRAPPER_PYTHON=/cm/shared/apps/python/2.7.6/bin/python
\t\tsource $ENV_DIR/bin/activate

\t\t# Prepare to install new python packages
\t\texport PATH=$ENV_DIR/install/bin:$PATH
\t\texport PYTHONPATH=$ENV_DIR/install/lib/python2.7/site-packages


cd /home/arendeiro/baf-kubicek/

pyatac vplot \
--bed {peaks} \
--bam {bam} \
--out {output_prefix}.vplot \
--cores 8 \
--lower 30 \
--upper 1000 \
--flank 500 \
--scale \
--plot_extra

pyatac sizes \
--bam {bam} \
--bed {peaks} \
--out {output_prefix}.sizes  \
--lower 30 \
--upper 1000

pyatac bias \
--fasta ~/resources/genomes/hg19/hg19.fa \
--bed {peaks} \
--out {output_prefix}.bias \
--cores 8

pyatac bias_vplot \
--bed {peaks} \
--bg {output_prefix}.bias.Scores.bedgraph.gz \
--fasta ~/resources/genomes/hg19/hg19.fa \
--sizes {output_prefix}.sizes.fragmentsizes.txt \
--out {output_prefix}.bias_vplot \
--cores 8 \
--lower 30 \
--upper 1000 \
--flank 500 \
--scale \
--plot_extra

date
""".format(
        name=name,
        log=log_file,
        peaks=bed_file,
        bam=bam_file,
        output_prefix=os.path.join(output_dir, name),
    )

    # write job to file
    with open(job_file, "w") as handle:
        handle.writelines(cmd)

    tk.slurm_submit_job(job_file)
