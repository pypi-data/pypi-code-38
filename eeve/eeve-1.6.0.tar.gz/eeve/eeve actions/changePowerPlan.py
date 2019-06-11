import subprocess
import sys

mappings = None


def get_power_plan_info(print_to_screen=True):
    global mappings
    proc = subprocess.Popen(["powercfg", "/l"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    result = str(out, 'utf-8').replace('\r', '').split('\n')[3:][:-1]
    result = [r.split(' ', 4)[3:] for r in result]
    mappings = {}
    active_plan = None
    for i in range(len(result)):
        temp_result = result[i][1].split('(', 1)[1:][0].split(')')
        result[i][1] = temp_result[0]
        mappings[result[i][1]] = result[i][0]
        if temp_result[1].replace(' ', '') == '*':
            active_plan = temp_result[0]
        if print_to_screen:
            print(">>", result[i])

    return mappings, active_plan


def set_power_plan(power_plan_name):
    if mappings is None:
        get_power_plan_info(print_to_screen=False)
    proc = subprocess.Popen(["powercfg", "/s", mappings[power_plan_name]], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    result2 = str(out, 'utf-8').replace('\r', '')
    #print(result2)


if __name__ == '__main__':
    _, active_plan = get_power_plan_info()
    print("Currently active:", active_plan)
    plan = input("power mode: ") if len(sys.argv) < 2 else sys.argv[1]
    set_power_plan(plan)
    _, active_plan = get_power_plan_info(print_to_screen=False)
    print("Set active:", active_plan)


class SetPowerPlan:
    def run(self, plan_name):
        _, active_plan = get_power_plan_info(print_to_screen=False)
        print("Last power plan:", active_plan)

        set_power_plan(plan_name)

        _, active_plan = get_power_plan_info(print_to_screen=False)
        print("Current power plan:", active_plan)


actions = {'set power plan': SetPowerPlan}
