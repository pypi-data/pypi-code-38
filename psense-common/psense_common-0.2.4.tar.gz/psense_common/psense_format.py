from datetime import datetime
import re


class psense_exp_title:
    def __init__(self):
        # process experiment Information
        self.typeof_study = dict({
            'H': 'Clinical',
            'F': 'Flow System',
            'B': 'Beaker',
            'A': 'Prototype',
            'R': 'Pre-Clinical',
        })

        self.typeof_sensor = dict({
            'G': 'Glucose',
            'O': 'Oxygen',
            'L': 'Lactate',
            'K': 'Ketone',
            'T': 'Temperature',
            'X': 'Other'
        })
        self.typeof_electrode = dict({
            'C': 'Circular',
            'R': 'Rectangular',
            'X': 'Other'
        })
        self.typeof_stack = dict({
            'R': 'Ring',
            'P': 'Planar',
            'X': 'Other',
        })
        self.typeof_process = dict({
            'S': 'Standard',
            'V': 'Volcano',
            'B': 'Blanket',
            '0': 'No Silicone',
        })
        self.typeof_extras = dict({
            'C': 'Catalase',
            'P': 'Peroxidase',
            'N': 'NAD+',
            'O': 'Other',
            'X': 'X'
        })

    def decode(self, expid):
        """translate a percusense experiment identifier string into a human-
        readble dictionary"""

        res = []
        try:
            regions = expid.upper().split('-')

            # simple validation
            for i in range(len(regions), 5):
                regions.append('')

            if len(regions[0]) > 4:
                study = {
                    'start': datetime.strptime('{}-{}-{}'.format(regions[0][:2], max(ord(regions[0][2:3]) - 64, 1), max(1, int(regions[0][3:5]))), '%y-%m-%d').date().isoformat(),
                    'type': self.typeof_study.get(regions[0][5:6]),
                    'run': regions[0][7:9],
                    'device': regions[0][9:]
                }

                # special cases -- 2-digit study type
                if regions[0][5:7] == 'AN':
                    study['type'] = 'Pre-Clinical'
                elif regions[0][5:7] == 'HU':
                    study['type'] = 'Clinical'

            else:
                study = []

            if len(regions[2]) > 0:
                sensor = {
                    'code': '{}-{}-{}'.format(regions[1], regions[2], regions[3]),
                    'type': self.typeof_sensor.get(regions[4][:1]),
                    'vsn': regions[4][1:3],
                    'electrode': self.typeof_electrode.get(regions[4][3:4]),
                    'stack': self.typeof_stack.get(regions[4][4:5]),
                    'process': self.typeof_process.get(regions[4][5:6]),
                    'extras': self.typeof_extras.get(regions[4][6:7], regions[4][6:7])
                }
            else:
                sensor = []

            res = dict(study=study, sensor=sensor)
        except:
            pass

        return res


"Simple IO Functions"


def yn_input(message, default='y'):
    "i/o: collect a yes/no answer from input"
    choices = 'Y/n' if default.lower() in ('y', 'yes') else 'y/N'
    choice = input("{} ({}) ".format(message, choices))
    values = ('y', 'yes', '') if choices == 'Y/n' else ('y', 'yes')
    return choice.strip().lower() in values


def answer_input(message, choices, default='0', is_required=True):
    "i/o: collect a typed answer from input (regex response validation)"
    is_valid = False

    if isinstance(choices, list):
        while not is_valid:
            choice_str = ", ".join(choices)
            choice = input("%s (%s)".format(message, choice_str)).strip().upper()
            if len(choice) == 0 and not is_required:
                return default
            elif (len(choice) > 0 and choice in choices):
                return choice

            print('Invalid Input ({})'.format(choice))

    elif isinstance(choices, str):
        while not is_valid:
            choice = input(message).strip().upper()
            if len(choice) == 0 and not is_required:
                return default
            elif (len(choice) > 0 and
                  choice in str(re.search(r'{}'.format(choices.upper()), choice))):

                return choice

            print('Invalid Input ({})'.format(choice))

    assert(False)


def exptype_input():
    "i/o: selection of starting a new experiment or resuming an existing one"
    message = '\nSelect experiment type and press enter\n\t[1] Start a new sensor (default)\n\t[2] Resume an existing sensor\n > '
    isvalid = False
    while not isvalid:
        choice = input(message).strip()
        if choice is '':
            return True
        elif choice.isnumeric():
            choice = int(choice)
            if choice == 2:
                return False
            else:
                return True
        else:
            print('Invalid input.')


def setup_new_experiment(device):
    "i/o: user input to generate a new percusense experiment id"
    assert isinstance(device, str), "device must be of type string"

    exp_beaker = answer_input('Specify the test system (A1, [B1], F1, AN, HU, etc): ', '([ABFP][0-9]|AN|HU){1}', 'ZZ', True)
    exp_run = int(answer_input('Specify the run number [1]: ', '[0-9]{1,2}', 1, False))
    exp_lot_we = int(answer_input('WE Lot # (required): ', '[0-9]{1,4}', 1, True))
    exp_lot_re = int(answer_input('CE/RE Lot # [000]: ', '[0-9]{0,3}', 0, False))
    exp_lot_sn = answer_input('Sensor ID [00]: ', '[A-Z0-9]{0,2}', '00', False)
    exp_type = answer_input('Sensor Type ([G]lucose, (O)xygen, (L)actate, (K)etone, (T)emp): ', '[GOLKT]', 'G', False)
    exp_vsn = int(answer_input('VSN Substrate Design ([1], 9, etc): ', '[0-9]{1,2}', '1', False))
    exp_discs = answer_input('Electrode Shape ([C]ircular, (R)ectangular): ', '[A-Z]{1}', 'C', False).strip().upper()
    exp_planar = answer_input('Substrate Information ([P]lanar, (R)ing): ', '[A-Z]{1}', 'P', False).strip().upper()
    exp_volcano = answer_input('Process Label ([V]olcano, (S)tandard, (B)lanket): ', '[A-Z]{1}', 'V', False).strip().upper()
    exp_addendum = answer_input('Additional Flag (1 character) [X]: ', '[A-Z0-9]{1}', 'X', False).strip().upper()

    expid = '{}{}{}{}{:02d}{:0>3.3}-{:04d}-{:03d}-{:.2}-{}{:02d}{}{}{}{}'.format(
        datetime.now().strftime('%y'),
        chr(int(datetime.now().strftime('%m')) + 64),
        datetime.now().strftime('%d'),
        exp_beaker,
        exp_run,
        device,
        exp_lot_we,
        exp_lot_re,
        exp_lot_sn.zfill(2),
        exp_type,
        exp_vsn,
        exp_discs,
        exp_planar,
        exp_volcano,
        exp_addendum).strip().upper()

    print('> done with data input. ')
    print('Experiment ID: {}'.format(expid))

    return expid
