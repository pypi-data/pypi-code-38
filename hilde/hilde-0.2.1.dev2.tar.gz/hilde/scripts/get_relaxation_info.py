# USAGE:  ./get_relaxation_info.py  aims.out (aims.out.2 ...)
#
# Revision 2018/08: FK
# 23/4/2019: give max. force in meV/AA instead of eV/AA

from argparse import ArgumentParser as argpars

parser = argpars(description="Summarize the relaxation path")
parser.add_argument("aimsouts", type=str, nargs="+", help="aims output files")
args = parser.parse_args()

# Find the optimizer type
def get_optimizer(f):
    try:
        line = next(l for l in f if "Geometry relaxation:" in l)
    except StopIteration:
        exit("Optimizer not found -- is this output from a relaxation?")

    if "Textbook BFGS" in line:
        return 1
    if "TRM" in line:
        return 2
    return -1


# find energy
def get_energy(f):
    line = next(l for l in f if "Total energy corrected" in l)
    total_energy = float(line.split()[5])
    line = next(l for l in f if "Electronic free energy" in l)
    free_energy = float(line.split()[5])
    return total_energy, free_energy


# get max_force
def get_forces(f):
    line = next(l for l in f if "Maximum force component" in l)
    return float(line.split()[4])


# get current volume
def get_volume(f):
    for line in f:
        if "| Unit cell volume " in line:
            return float(line.split()[5])
        if "Begin self-consistency loop:" in line:
            return -1
        if "Final output of selected total energy values:" in line:
            return -1


# parse info of one step
def parser(f, n_init=0, optimizer=2):
    n_rel = n_init
    converged = 0
    abort = 0
    while not converged and not abort:
        n_rel += 1
        status = 0
        try:
            energy, free_energy = get_energy(f)
            max_force = get_forces(f)
        except StopIteration:
            break

        for line in f:
            if "Present geometry is converged." in line:
                converged = 1
                break
            elif "Advancing" in line:
                pass
            elif "Aborting optimization" in line:
                abort = 1
            elif "Counterproductive step -> revert!" in line:
                status = 1
            elif "Optimizer is stuck" in line:
                status = 2
            #            elif '**' in line:
            #                status = 3
            elif "Finished advancing geometry" in line:
                volume = get_volume(f)
                break
            elif "Updated atomic structure" in line:
                volume = get_volume(f)
                break
        yield n_rel, energy, free_energy, max_force, volume, status, converged, abort


def print_status(n_rel, energy, de, free_energy, df, max_force, volume, status_string):
    """ Print the status line, skip volume if not found """

    if volume and volume > 0:
        vol_str = f"{volume:15.4f}"
    else:
        vol_str = ""

    print(
        "{:5d}   {:16.8f}   {:16.8f} {:14.6f} {:20.6f} {} {}".format(
            n_rel, energy, free_energy, df, max_force * 1000, vol_str, status_string
        )
    )


def main():
    init, n_rel, converged, abort = 4 * (None,)
    status_string = [
        "",
        "rejected.",
        "rejected: force <-> energy inconsistency?",
        "stuck.",
    ]

    # Run
    print(
        "\n# Step Total energy [eV]   Free energy [eV]   F-F(1)"
        + " [meV]   max. force [meV/AA]  Volume [AA^3]\n"
    )

    for infile in args.aimsouts:
        with open(infile) as f:
            # Check optimizer
            optimizer = get_optimizer(f)
            ps = parser(f, n_init=n_rel or 0, optimizer=optimizer)
            for (n_rel, ener, free_ener, fmax, vol, status, converged, abort) in ps:
                if not init:
                    first_energy, first_free_energy = ener, free_ener
                    init = 1
                print_status(
                    n_rel,
                    ener,
                    1000 * (ener - first_energy),
                    free_ener,
                    1000 * (free_ener - first_free_energy),
                    fmax,
                    vol,
                    status_string[status],
                )

    if converged:
        print("--> converged.")
    if abort:
        print("*--> aborted, too many steps.")


if __name__ == "__main__":
    main()
