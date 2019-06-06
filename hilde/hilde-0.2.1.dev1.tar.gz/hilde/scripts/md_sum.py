""" Summarize output from ASE.md class (in md.log) """

from pathlib import Path
from argparse import ArgumentParser
import numpy as np

from hilde.trajectory import reader


def parse_log(filename):
    """ parse the ASE logfile, typically md.log """
    e_kin = []
    e_pot = []
    temp = []
    time = []
    with open(filename) as f:
        for line in f:
            if line.strip() == "":
                continue
            if "Time" in line:
                continue

            t, _, ep, ek, T = (float(l) for l in line.split())
            time.append(t)
            temp.append(T)
            e_kin.append(ek)
            e_pot.append(ep)

    return e_kin, e_pot, temp, time


def main():
    """ main routine """
    parser = ArgumentParser(description="Read md.log and make simple statistics")
    parser.add_argument("file", help="md.log or trajectory.son input file")
    parser.add_argument("-p", "--plot", action="store_true", help="plot to pdf")
    parser.add_argument("--avg", type=int, help="running avg in plot", default=100)
    parser.add_argument("-v", "--verbose", action="store_true", help="give more info")
    args = parser.parse_args()

    infile = Path(args.file)

    if "yaml" in infile.suffix:
        trajectory = reader(infile)[1:]
        e_kin = [atoms.get_kinetic_energy() for atoms in trajectory]
        e_pot = [atoms.get_potential_energy() for atoms in trajectory]
        temp = [atoms.get_temperature() for atoms in trajectory]
        # sum up time steps, necessary if dt changes during md
        time = np.cumsum([atoms.info["dt_fs"] * 0.001 for atoms in trajectory])
    elif "log" in infile.suffix:
        e_kin, e_pot, temp, time = parse_log(infile)

    if args.verbose:
        n_range = min(20, len(trajectory) - 2)
        print(f"step   time   temperature")
        for ii in range(n_range):
            print(
                f'{trajectory[-n_range+ii].info["nsteps"]:5d} '
                f"{time[-n_range+ii]:10.4f} "
                f"{temp[-n_range+ii]:10.4f} "
            )

    # divide into three thirds
    len_3 = len(temp) // 3
    temp_1 = temp[:len_3]
    temp_2 = temp[len_3 : 2 * len_3]
    temp_3 = temp[2 * len_3 :]

    print(f"Simulation time:         {time[-1] - time[0]:.4f} ps ({len(time)} steps)")
    print(f"Temperature:             {np.mean(temp):.2f} +/- {np.std(temp):.2f}K")
    print(f"Temperature (1st 1/3):   {np.mean(temp_1):.2f} +/- {np.std(temp_1):.2f}K")
    print(f"Temperature (2nd 1/3):   {np.mean(temp_2):.2f} +/- {np.std(temp_2):.2f}K")
    print(f"Temperature (3rd 1/3):   {np.mean(temp_3):.2f} +/- {np.std(temp_3):.2f}K")
    print(f"Kinetic energy:          {np.mean(e_kin):.2f} +/- {np.std(e_kin):.2f}eV")
    print(f"Potential energy:        {np.mean(e_pot):.2f} +/- {np.std(e_pot):.2f}eV")

    if args.plot:
        import matplotlib

        matplotlib.use("pdf")

        from matplotlib import pyplot as plt
        import pandas as pd

        from hilde.helpers.plotting import tableau_colors as tc

        # plot temperatures
        data = pd.Series(temp, time)

        fig, (ax, ax2) = plt.subplots(ncols=2)

        # settings for the immediate plot
        plot_settings = {"alpha": 0.4, "linewidth": 1.0, "label": ""}
        avg_settings = {"linewidth": 1.5}

        data.plot(color=tc[0], title="Nuclear Temperature", ax=ax, **plot_settings)

        roll = data.rolling(window=args.avg, min_periods=0).mean()
        roll.plot(color=tc[0], label=f"T_nucl", ax=ax, **avg_settings)

        # exp = data.iloc[min(len(data) // 2, args.avg) :].expanding().mean()
        # exp.plot( color=tc[5], label=f"Expanding mean ({args.avg}", ax=ax)

        ax.set_xlabel("Time [ps]")
        ax.set_ylabel("Nucl. Temperature [K]")
        ax.legend()

        # fig.savefig("temp.pdf")

        # plot energies in one plot
        # fig, ax = plt.subplots()

        e_kin = pd.Series(e_kin, time)
        # e_kin -= e_kin.min()

        e_pot = pd.Series(e_pot, time)
        e_pot -= e_pot.min()

        e_tot = e_pot + e_kin
        e_dif = e_pot - e_kin

        e_tot.plot(color=tc[0], title="Total Energy", ax=ax2, **plot_settings)
        roll = e_tot.rolling(window=args.avg, min_periods=0).mean()
        roll.plot(color=tc[0], ax=ax2, label="E_tot", **avg_settings)

        e_pot.plot(color=tc[3], ax=ax2, **plot_settings)
        roll = e_pot.rolling(window=args.avg, min_periods=0).mean()
        roll.plot(color=tc[3], ax=ax2, label="E_pot", **avg_settings)

        ax2.axhline(0, linewidth=1, color="k")
        e_dif.plot(color=tc[1], ax=ax2, **plot_settings)
        exp = e_dif.rolling(min_periods=0, window=args.avg).mean()
        exp.plot(color=tc[1], ax=ax2, label="E_pot - E_kin", **avg_settings)

        ax2.legend()
        ax2.set_xlabel("Time [ps]")
        ax2.set_ylabel("Energy [eV]")

        # fig.tight_layout()
        fname = "md_summary.pdf"
        fig.savefig(fname)
        print(f".. summary plotted to {fname}")


if __name__ == "__main__":
    main()
