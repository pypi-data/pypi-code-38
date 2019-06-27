from pyehub.outputter import to_dataframes
import pickle
import pandas as pd
import matplotlib.pyplot as plt
# import seaborn as sns

# sns.set()


def plot_energy_balance(results: dict) -> None:
    pass


def plot_storage(results: dict, pl_state=True, pl_gross_ch=True, pl_gross_dch=True,
                 pl_net_ch=True, pl_net_dch=True, pl_decay=True) -> None:
    """
    Plots various parameters related to storages:
    storage state: The level of energy remaining in the storage
    gross charge(charge from stream): Energy sent to storage from stream for charging
    gross discharge(discharge to stream): Energy going into stream after discharging
    net charge: Energy actually reaching storage(after loss of gross charge due to charging efficiency)
    net discharge: Energy actually leaving storage(after loss from this due to discharging efficiency, it becomes gross discharge)
    decay loss(standing loss): Energy dissipating due to standing losses
    Args:
        results: the 'results' dictionary returned by solve() method 
        pl_state: boolean value; whether to plot 'storage state' or not
        pl_gross_ch: boolean value; whether to plot 'gross charge' or not
        pl_gross_dch: boolean value; whether to plot 'gross discharge' or not
        pl_net_ch: boolean value; whether to plot 'net charge' or not
        pl_net_dch: boolean value; whether to plot 'net discharge' or not
        pl_decay: boolean value; whether to plot 'decay loss' or not
    """
    solution_section = results['solution']
    attributes = to_dataframes(solution_section)

    for storage in attributes['storages']:
        ax = plt.gca()

        ser_storage_state = attributes['storage_level'][storage]
        ser_gross_charge = attributes['energy_to_storage'][storage]
        ser_gross_discharge = -attributes['energy_from_storage'][storage]

        eff_charge = attributes['CHARGING_EFFICIENCY']['CHARGING_EFFICIENCY'][storage]
        eff_discharge = attributes['DISCHARGING_EFFICIENCY']['DISCHARGING_EFFICIENCY'][storage]
        decay = attributes['STORAGE_STANDING_LOSSES']['STORAGE_STANDING_LOSSES'][storage]
        capacity = attributes['capacity_storage']['capacity_storage'][storage]

        ser_net_discharge = 0
        ser_net_charge = ser_gross_charge.multiply(eff_charge)
        if eff_discharge != 0:
            ser_net_discharge = ser_gross_discharge.divide(eff_discharge)
        decay_loss = -ser_storage_state.multiply(decay)[:-1]

        d = {'storage state': ser_storage_state, 'charge from stream': ser_gross_charge, 'net charge': ser_net_charge,
             'discharge to stream': ser_gross_discharge, 'net discharge': ser_net_discharge, 'standing loss': decay_loss}
        df = pd.DataFrame(data=d)

        if capacity != 0:
            df = (df.div(capacity)).mul(100)

        # since we need to set x and y labels and user may not want to plot any parameter, we assign all plots to pl
        # if any plot was assigned to pl, we set its x and y labels
        # because all plots have same axes, we get it for all p
        if pl_state:
            pl = df['storage state'].plot(kind='bar', xticks=df.index, title=storage, ax=ax, color='deepskyblue', legend=True)
        if pl_gross_ch:
            pl = df['charge from stream'].plot(drawstyle='steps-post', xticks=df.index, title=storage, color='lightgreen',
                                    linewidth=3, ax=ax, legend = True)
        if pl_net_ch:
            pl = df['net charge'].plot(drawstyle='steps-post', xticks=df.index, title=storage, color='green',
                                    linestyle='--', linewidth=2, ax=ax, legend=True)
        if pl_gross_dch:
            pl = df['discharge to stream'].plot(drawstyle='steps-post', xticks=df.index, title=storage, color='orange',
                                    linewidth=3, ax=ax, legend=True)
        if pl_net_dch:
            pl = df['net discharge'].plot(drawstyle='steps-post', xticks=df.index, title=storage, color='red',
                                    linestyle='--', linewidth=2, ax=ax, legend=True)
        if pl_decay:
            pl = df['standing loss'].plot(kind='bar', xticks=df.index, title=storage, color='saddlebrown',
                                          ax=ax, legend=True)

        if pl_state or pl_gross_ch or pl_net_ch or pl_gross_dch or pl_net_dch or pl_decay:
            plt.legend(loc='best')
            pl.set_xlabel("Time")
            pl.set_ylabel("Storage state(in %)")
            plt.show()


def main():
    with open('model1.results', 'rb') as results_file:
        results = pickle.load(results_file)
    plot_storage(results)


if __name__ == '__main__':
    main()



    # current_palette = sns.color_palette()
    # sns.palplot(current_palette)

# df_storage_state = attributes['storage_level']
# df_storage_state.plot(kind='line', y=storage, ax=ax, xticks=attributes['time'], yticks=ser_storage_state)
# df_gross_charge = attributes['energy_to_storage']
# df_gross_charge.plot(kind='line', y=storage, ax=ax, yticks=ser_gross_charge)
# df_discharging = -attributes['energy_from_storage']
# df_discharging.plot(kind='line', y=storage, ax=ax, yticks=df_discharging[storage])
# # df.plot(kind='line', y='Hot Water Tank', color='red', ax=ax)
# plt.show()

# list_for_yticks = ser_storage_state.tolist() + ser_gross_charge.tolist() + ser_gross_discharge.tolist()
        # list_for_yticks = list(dict.fromkeys(list_for_yticks))


# list_for_yticks = list_for_yticks/capacity * 100

# df.drop(['storage_state'], axis=1).plot(drawstyle='steps-post',color=('green','red'),linewidth=2, ax=ax,)

 # overlay.set_xlim(right=10)
        # overlay.grid(marker='x')
