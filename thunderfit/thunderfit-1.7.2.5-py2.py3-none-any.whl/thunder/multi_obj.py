from obj import *
import glob
import copy
import pandas
from tqdm import tqdm


# TODO
# make option of passing in many params files - one for each data file

class ThunderBag():

    def __init__(self, input):
        # initialise everything first
        self.thunder_bag: {} = {}

        if isinstance(input, Thunder):  # if only pass one but its already a thunder object then just use that
            self.overwrite_thunder(input)  # add all the details in depending on args
        elif isinstance(input, dict):
            self.create_bag(input)  # add all the details in depending on args
        else:
            raise TypeError('Cannot convert input to Thunder object')

    def overwite_thunder(self, inp):
        thun = inp
        self.x_ind = thun.x_ind
        self.y_ind = thun.y_ind
        self.e_ind = thun.e_ind
        self.x_label = thun.x_label
        self.y_label = thun.y_label
        self.datapath = thun.datapath
        self.user_params = thun.user_params

    def create_bag(self, inp):
        self.x_label = inp['x_label']
        self.y_label = inp['y_label']
        self.e_label = inp['e_label']
        self.x_ind =  inp['x_ind']
        self. y_ind = inp['y_ind']
        self.e_ind = inp['e_ind']
        self.user_params = inp['fit_params']
        self.img_path = inp['imgpath']

        assert isinstance(inp['datapath'], list), "Wrong format for datapath, should be a list"
        self.datapath = inp['datapath']

        for i, data in tqdm(enumerate(self.datapath)):
            if isinstance(data, Thunder):
                self.thunder_bag[i] = data
            elif isinstance(data, str):
                # then read the data file
                if '*' in data:
                    filematches = glob.glob(data)
                    for j, file in enumerate(filematches):
                        try:
                            self.thunder_bag[f'{i}_{j}'] = self.create_thunder(file, inp) # make a thunder object for each file
                        except pandas.errors.ParserError as e:
                            logging.warn(f"A Thunder object could not be created for the datafile: {file}, skipping")
                else:
                    try:
                        self.thunder_bag[str(i)] = self.create_thunder(data, inp)
                    except pandas.errors.ParserError as e:
                        logging.warn(f"A Thunder object could not be created for the datafile: {file}, skipping")
            else:
                logging.warn(f"wrong format in data list detected for {i}th element: {data}. Skipping element")
                pass

    @staticmethod
    def create_thunder(file, inp):
        arguments = copy.deepcopy(inp)
        arguments['datapath'] = file
        thund_obj = Thunder(arguments)
        return thund_obj

    @staticmethod
    def fit_bag(bag_dict):
        for baglabel, thund in tqdm(bag_dict.items()):
            thund.background_finder()  # then determine the background
            specified_dict = peak_details(thund.user_params)
            thund.peaks_unspecified(specified_dict)

            # now fit peaks
            thund.fit_peaks()
            #thund.plot_all()
            thund.fit_report()

        return bag_dict

def main(arguments):

    bag = ThunderBag(copy.deepcopy(arguments)) # load object

    bag.fit_bag(bag.thunder_bag)
    import ipdb
    ipdb.set_trace()


    return bag


def parse_param_file(filepath='./bag_params.txt'):
    """
    parse a params file which we assume is a dictionary
    :param filepath: str: path to params file
    :return: dictionary of paramters
    """
    # maybe use json loads if you end up writing parameter files non-manually

    with open(filepath, 'r') as f:
        arguments = json.load(f)
        f.close()

    # TODO: add some checks to user passed data
    return arguments

if __name__ == '__main__':

    ##### for saving and parsing
    def parse_args(arg):
        """
        convert argparse arguments into a dictionary for consistency later
        :param arg: argparse parsed args
        :return: dictionary of parameters
        """
        arguments = {}
        arguments['x_label'] = arg.x_label
        arguments['y_label'] = arg.y_label
        arguments['e_label'] = arg.y_label
        arguments['x_ind'] = arg.x_ind
        arguments['y_ind'] = arg.y_ind
        arguments['e_ind'] = arg.e_ind
        arguments['datapath'] = arg.datapath
        arguments['user_params'] = arg.user_params
        arguments['imgpath'] = arg.imgpath

        # TODO: add some checks to user passed data

        return arguments

    def make_dir(dirname, i=1):
        """
        function to make a directory, recursively adding _new if that name already exists
        :param dirname: str: name of directory to create
        :param i: the run number we are on
        :return: str: the directory name which was available, and all subsequent data should be saved in
        """
        try:
            os.mkdir(f'{dirname}')
        except FileExistsError as e:
            dirname = make_dir(f'{dirname}_new', i + 1)
            if i == 1:
                print(e, f' so I named the file: {dirname}')
            return dirname
        return dirname
    #####


    # i.e. called from bash
    import argparse

    parser = argparse.ArgumentParser(
        description='fit peaks and background to the given data given a set of parameter'
    )
    parser.add_argument('--param_file_path', type=str, default='./bag_params.txt',
                        help='input filepath to param file, if you want to use it, if you use this no other inputs will '
                             'be parsed')
    parser.add_argument('--x_label', type=str, default='x_axis',
                        help='the label for independent variables')
    parser.add_argument('--y_label', type=str, default='y_axis',
                        help='the label for dependent variables')
    parser.add_argument('--e_label', type=str, default='y_error',
                        help='the label for uncertainties in y')
    parser.add_argument('--x_ind', type=int, default=0,
                        help='the column in data which is the independent data')
    parser.add_argument('--y_ind', type=int, default=1,
                        help='the column in data which is the dependent data')
    parser.add_argument('--e_ind', type=Union[int, None], default=None,
                        help='the column in data which is the independent data uncertainties')
    parser.add_argument('--datapath', type=str, default=['./data.txt'],
                        help='relative paths to the datafiles from where python script is called, a list of paths')
    parser.add_argument('--imgpath', type=str, default=['./data.txt'],
                        help='relative path to the image file for the scans - if it exists')
    parser.add_argument('--user_params', type=Dict, default={'yfit': None, 'background': None, 'peak_types': [],
                                                             'peak_centres': [], 'peak_widths': [], 'peak_amps': [],
                                                             'chisq': None, 'free_params': None,
                                                             'p_value': None, 'tightness': None},
                        help='the fit data as specified in the Thunder __init__')
    args = parser.parse_args()  # this allows us to now use them all

    if args.param_file_path: # if there is a params file then use it
        LOGGER.info('Using params file')
        arguments = parse_param_file(args.param_file_path) # parse it
    else:
        print('not using params file')
        arguments = parse_args(args) # else use argparse but put in dictionary form

    main(arguments)


    # now save things!