import numpy as np
from datetime import timedelta
import os.path

DEUTERIUM = "deuterium"
OXYGEN = "oxygen"

D_VSMOW_RATIO = 0.00015576
O18_VSMOW_RATIO = 0.0020052
STANDARD_WATER_MOL_MASS = 18.10106 / 1000  # kg
PPM_TO_RATIO = 1 / 1000000
POP_DIL_SPACE_D = 1.041
POP_DIL_SPACE_O = 1.007
STD_POP_AVG_RDIL = 1.02
FAT_FREE_MASS_FACTOR = 0.73
HOURS_PER_DAY = 24
LITERS_PER_MOL = 22.414
WEIR_CONSTANT = 5.7425
MJ_PER_KCAL = 4.184 / 1000

D_PLATEAU_LIMIT = 5.0
O18_PLATEAU_LIMIT = 5.0
DIL_SPACE_RATIO_LOW_LIMIT = 1.00
DIL_SPACE_RATIO_HIGH_LIMIT = 1.07
KO_KD_RATIO_LOW_LIMIT = 1.1
KO_KD_RATIO_HIGH_LIMIT = 1.7


class DLWSubject:
    """Class for performing Doubly Labeled Water calculations
       Attributes:
           d_meas (np.array): deuterium values as measured (can be in permil or ppm)
           o18_meas (np.array): oxygen 18 values as measured (can be in permil or ppm)
           d_deltas (np.array): deuterium delta values of subject samples
           o18_deltas (np.array): oxygen 18 delta values of subject samples
           sample_datetimes ([datetime]): dates and times of sample collections and dose
                                        should be in order of background, dose, PD4, PD5, ED4, ED5
           dose_weights ([float]): weights in g of doses administered, deuterium first, 18O second
           mixed_dose ([bool]): boolean indicating whether doses are mixed together or separate
           mol_masses ([float]): molecular masses in g/mol of doses administered, deuterium first, 18O second
           dose_enrichments ([float]): dose enrichments in ratio of doses administered, deuterium first, 18O second
           subject_weights ([float]): initial and final weights of the subject in kg
           subject_id ([string]): string identifier for the data
           pop_avg_rdil ([float]): population average dilution space ratio, if provided
           in_permil ([bool]): True if measured d and O18 are in permil, false if they are in ppm
           d_ratios (np.array): deuterium ratios of subject samples
           o18_ratios (np.array): 18O ratios of subject samples
           kd_per_hr (float): deuterium turnover rate in 1/hr
           ko_per_hr (float): oxygen turnover rate in 1/hr
           ko_kd_ratio (float): ratio of oxygen and deuterium turnover rates
           nd (dict): dictionary containing all the calculated values of the deuterium dilution space
                plat_a_mol (float): calculated by the plateau method using the a sample in mol
                plat_b_mol (float): calculated by the plateau method using the b sample in mol
                plat_avg_mol (float): the average of the a and b plateau dilution spaces in mol
                int_a_mol (float): calculated by the intercept method using the a sample in mol
                int_b_mol (float): calculated by the intercept method using the b sample in mol
                int_avg_mol (float): the average of the a and b intercept dilution spaces in mol
                adj_plat_avg_mol (float): average plateau dilution space adjusted for the subject weight change over
                           the sampling period, in mol
                adj_int_avg_mol (float): average intercept dilution space adjusted for the subject weight change over
                           the sampling period, in mol
                adj_plat_avg_kg (float): average plateau dilution space adjusted for the subject weight change over
                           the sampling period, in kg
                adj_int_avg_kg (float): average intercept dilution space adjusted for the subject weight change over
                           the sampling period, in kg
           no (dict): dictionary containing all the calculated values of the oxygen 18 dilution space
                plat_a_mol (float): calculated by the plateau method using the a sample in mol
                plat_b_mol (float): calculated by the plateau method using the b sample in mol
                plat_avg_mol (float): the average of the a and b plateau dilution spaces in mol
                int_a_mol (float): calculated by the intercept method using the a sample in mol
                int_b_mol (float): calculated by the intercept method using the b sample in mol
                int_avg_mol (float): the average of the a and b intercept dilution spaces in mol
                adj_plat_avg_mol (float): average plateau dilution space adjusted for the subject weight change over
                           the sampling period, in mol
                adj_int_avg_mol (float): average intercept dilution space adjusted for the subject weight change over
                           the sampling period, in mol
                adj_plat_avg_kg (float): average plateau dilution space adjusted for the subject weight change over
                           the sampling period, in kg
                adj_int_avg_kg (float): average intercept dilution space adjusted for the subject weight change over
                           the sampling period, in kg
           dil_space_ratio (float): ratio of the 4 hr plateau deuterium and 18O dilution spaces
           total_body_water_d_kg (float): total body water calculated from the average D plateau dilution space, in kg
           total_body_water_o_kg (float): total body water calculated from the average 18O plateau dilution space, in kg
           total_body_water_ave_kg (float): average of total_body_water_d_kg and total_body_water_o_kg, in kg
           fat_free_mass_kg (float): fat free mass of the subject, in kg
           fat_mass_kg (float): fat mass of the subject, in kg
           body_fat_percent (float): body fat percent of the subject, in percent
           schoeller (dict): dictionary containing all the values calculated using the equation of Schoeller (equation
                            A6, 1986 as updated in 1988)
                co2_int (float): CO2 production rate in mol/hr using the weight adjusted, average, intercept dilution spaces
                co2_plat (float): CO2 production rate in mol/hr using the weight adjusted, average, plateau dilution spaces
                co2_int_mol_day (float): CO2 production rate in mol/day using the weight adjusted, average, intercept dilution spaces
                co2_int_L_hr (float): CO2 production rate in L/hr using the weight adjusted, average, intercept dilution spaces
                tee_int_kcal_day (float): Total energy expenditure calculated using the equation of Weir (1949) from co2
                            values calculated via Schoeller and the weight adjusted, average, intercept dilution spaces,
                            in kcal/day
                tee_plat_kcal_day (float): Total energy expenditure calculated using the equation of Weir (1949) from co2
                              values calculated via Schoeller and the weight adjusted, average, plateau dilution spaces,
                              in kcal/day
                tee_int_mj_day (float): Total energy expenditure calculated using the equation of Weir (1949) from
                            co2 values calculated via Schoeller and the weight adjusted, average, intercept dilution
                            spaces, in mj/day
                tee_plat_mj_day (float): Total energy expenditure calculated using the equation of Weir (1949) from
                            co2 values calculated via Schoeller and the weight adjusted, average, plateau dilution
                            spaces, in mj/day
            racette (dict): dictionary containing all the values calculated using the equation of Racette, eqn 1 (1994)
                co2_int (float): CO2 production rate in mol/hr using the weight adjusted, average, intercept dilution spaces
                co2_plat (float): CO2 production rate in mol/hr using the weight adjusted, average, plateau dilution spaces
                co2_int_mol_day (float): CO2 production rate in mol/day using the weight adjusted, average, intercept dilution spaces
                co2_int_L_hr (float): CO2 production rate in L/hr using the weight adjusted, average, intercept dilution spaces
                tee_int_kcal_day (float): Total energy expenditure calculated using the equation of Weir (1949) from co2
                            values calculated via Racette and the weight adjusted, average, intercept dilution spaces,
                            in kcal/day
                tee_plat_kcal_day (float): Total energy expenditure calculated using the equation of Weir (1949) from co2
                              values calculated via Racette and the weight adjusted, average, plateau dilution spaces,
                              in kcal/day
                tee_int_mj_day (float): Total energy expenditure calculated using the equation of Weir (1949) from
                            co2 values calculated via Racette and the weight adjusted, average, intercept dilution
                            spaces, in mj/day
                tee_plat_mj_day (float): Total energy expenditure calculated using the equation of Weir (1949) from
                            co2 values calculated via Racette and the weight adjusted, average, plateau dilution
                            spaces, in mj/day
            speakman (dict): dictionary containing all the values calculated using the equation of Speakman, eqn 17.41 (1997)
                co2_int (float): CO2 production rate in mol/hr using the weight adjusted, average, intercept dilution spaces
                co2_plat (float): CO2 production rate in mol/hr using the weight adjusted, average, plateau dilution spaces
                co2_int_mol_day (float): CO2 production rate in mol/day using the weight adjusted, average, intercept dilution spaces
                co2_int_L_hr (float): CO2 production rate in L/hr using the weight adjusted, average, intercept dilution spaces
                tee_int_kcal_day (float): Total energy expenditure calculated using the equation of Weir (1949) from co2
                            values calculated via Speakman and the weight adjusted, average, intercept dilution spaces,
                            in kcal/day
                tee_plat_kcal_day (float): Total energy expenditure calculated using the equation of Weir (1949) from co2
                              values calculated via Speakman and the weight adjusted, average, plateau dilution spaces,
                              in kcal/day
                tee_int_mj_day (float): Total energy expenditure calculated using the equation of Weir (1949) from
                            co2 values calculated via Speakman and the weight adjusted, average, intercept dilution
                            spaces, in mj/day
                tee_plat_mj_day (float): Total energy expenditure calculated using the equation of Weir (1949) from
                            co2 values calculated via Speakman and the weight adjusted, average, plateau dilution
                            spaces, in mj/day
           d_ratio_percent (float): Percent difference between the a and b delta measurements of deuterium
           o18_ratio_percent (float): Percent difference between the a and b delta measurements of 18O
           ee_check (float): Data quality check consisting of the percent difference between the TEE (in kcal/day)
                            calculated using the PD4/ED4 pair and the TEE calculated using the PD5/ED5 pair, both with
                            the plateau method.
    """

    def __init__(self, d_meas, o18_meas, sample_datetimes, dose_weights, mixed_dose, dose_enrichments,
                 subject_weights, subject_id, in_permil=True, pop_avg_rdil=None):
        """Constructor for the DLWSubject class
           :param d_meas (np.array): deuterium delta values of subject samples
           :param o18_meas (np.array): oxygen 18 delta values of subject samples
           :param sample_datetimes ([datetime]): dates and times of sample collections
           :param dose_weights ([float]): weights in g of doses administered, deuterium first, 18O second
           :param mixed_dose ([bool]): boolean indicating whether doses are mixed together or separate
           :param dose_enrichments ([float]): dose enrichments in ppm of doses administered, deuterium first, 18O second
           :param subject_weights ([float]): initial and final weights of the subject in kg
           :param subject_id ([string]): string identifier for the data
           :param in_permil ([bool]): True if measured d and O18 are in permil, false if they are in ppm
           :param pop_avg_rdil ([float]): population average dilution space to use in the calculations
        """
        if len(d_meas) == len(o18_meas) == len(sample_datetimes)-1 == 5:

            self.sample_datetimes = sample_datetimes
            self.dose_weights = dose_weights
            self.mixed_dose = mixed_dose
            self.dose_enrichments = np.array(dose_enrichments) / 1000000  # convert from ppm to ratio
            self.subject_weights = subject_weights
            self.subject_id = subject_id

            if pop_avg_rdil is None:
                self.pop_avg_rdil = STD_POP_AVG_RDIL
            else:
                self.pop_avg_rdil = pop_avg_rdil

            if (in_permil):
                self.d_deltas = d_meas
                self.o18_deltas = o18_meas
                self.d_ratios = self.d_deltas_to_ratios()
                self.o18_ratios = self.o18_deltas_to_ratios()
            else:
                self.d_ratios = d_meas * PPM_TO_RATIO
                self.o18_ratios = o18_meas * PPM_TO_RATIO
                self.d_deltas = self.d_ratios_to_deltas()
                self.o18_deltas = self.o18_ratios_to_deltas()

            self.kd_per_hr = self.average_turnover_2pt(self.d_ratios, self.sample_datetimes)
            self.ko_per_hr = self.average_turnover_2pt(self.o18_ratios, self.sample_datetimes)
            self.ko_kd_ratio = self.ko_per_hr / self.kd_per_hr

            self.mol_masses = self.calculate_mol_masses(self.dose_enrichments, self.mixed_dose)

            self.nd = self.calculate_various_nd()
            self.no = self.calculate_various_no()

            self.dil_space_ratio = self.nd['plat_a_mol'] / self.no['plat_a_mol']  # dilution space ratio err flag

            # self.rh2o = (self.nd['adj_plat_avg_kg'] * self.kd_per_hr * HOURS_PER_DAY) / STANDARD_WATER_MOL_MASS

            self.total_body_water_d_kg = self.nd['adj_plat_avg_kg'] / POP_DIL_SPACE_D
            self.total_body_water_o_kg = self.no['adj_plat_avg_kg'] / POP_DIL_SPACE_O
            self.total_body_water_ave_kg = (self.total_body_water_d_kg + self.total_body_water_o_kg) / 2
            # average total body water

            self.fat_free_mass_kg = self.total_body_water_ave_kg / FAT_FREE_MASS_FACTOR
            self.fat_mass_kg = self.subject_weights[0] - self.fat_free_mass_kg
            self.body_fat_percent = self.fat_mass_kg / self.subject_weights[0] * 100

            self.schoeller = self.calculate_schoeller()
            self.racette = self.calculate_racette()
            self.speakman = self.calculate_speakman()

            self.d_ratio_percent = self.percent_difference(self.d_ratios[1] - self.d_ratios[0],
                                                           self.d_ratios[2] - self.d_ratios[0])
            # err flag 2 h plateau < 5%
            self.o18_ratio_percent = self.percent_difference(self.o18_ratios[1] - self.o18_ratios[0],
                                                             self.o18_ratios[2] - self.o18_ratios[0])
            # err flag o18 plateau < 5%
            self.ee_check = self.ee_consistency_check()  # err flag # 4 pd4

        else:
            raise ValueError('Arrays not correct size')

    def d_deltas_to_ratios(self):
        """Convert deuterium delta values to ratios.
           :return: deuterium ratios
        """
        return ((self.d_deltas / 1000) + 1) * D_VSMOW_RATIO

    def o18_deltas_to_ratios(self):
        """Convert 18O delta values to ratios.
           :return: 18O ratios
        """
        return ((self.o18_deltas / 1000) + 1) * O18_VSMOW_RATIO

    def d_ratios_to_deltas(self):
        """Convert deuterium ratio values to delta.
           :return: deuterium deltas
        """
        return (self.d_ratios / D_VSMOW_RATIO - 1) * 1000

    def o18_ratios_to_deltas(self):
        """Convert 18O ratio values to deltas.
           :return: 18O deltas
        """
        return ((self.o18_ratios / O18_VSMOW_RATIO - 1) * 1000)

    @staticmethod
    def isotope_turnover_2pt(background, initratio, finalratio, elapsedhours):
        """Calculate an isotope turnover rate in 1/hr using the 2pt method
           :param background:  enrichment of the background urine measurement as a ratio
           :param initratio: enrichment of the initial urine measurement as a ratio
           :param finalratio: enrichment of the final urine measurement as a ratio
           :param elapsedhours: elapsed time in hours between the intial and final urine measurements
           :return: istope turnover rate in 1/hr
        """
        if (background < initratio and background < finalratio and finalratio < initratio):
            return (np.log(initratio - background) - np.log(finalratio - background)) / elapsedhours
        else:
            raise ValueError('Isotope ratios do not conform to pattern background < final < plateau')

    def average_turnover_2pt(self, ratios, sampledatetime):
        """Calculate the average isotope turnover rate in 1/hr using the 2pt method
           :param ratios: measured urine isotope ratios
           :param sampledatetime: time and date of urine collections
           :return: average isotope turnover rate in 1/hr
        """
        turnovers = np.zeros(4)

        elapsedhours = (timedelta.total_seconds(sampledatetime[4] - sampledatetime[2])) / 3600
        turnovers[0] = self.isotope_turnover_2pt(ratios[0], ratios[1], ratios[3], elapsedhours)

        elapsedhours = (timedelta.total_seconds(sampledatetime[5] - sampledatetime[2])) / 3600
        turnovers[1] = self.isotope_turnover_2pt(ratios[0], ratios[1], ratios[4], elapsedhours)

        elapsedhours = (timedelta.total_seconds(sampledatetime[4] - sampledatetime[3])) / 3600
        turnovers[2] = self.isotope_turnover_2pt(ratios[0], ratios[2], ratios[3], elapsedhours)

        elapsedhours = (timedelta.total_seconds(sampledatetime[5] - sampledatetime[3])) / 3600
        turnovers[3] = self.isotope_turnover_2pt(ratios[0], ratios[2], ratios[4], elapsedhours)
        return np.mean(turnovers)

    @staticmethod
    def calculate_mol_masses(dose_enrichments, mixed_dose):
        """ Calculate the molecular masses for the enriched dose waters
            :param: dose_enrichments ([float]):dose enrichments in ppm of doses administered, 2H first, 18O second
            :param: mixed_dose ([bool]): boolean indicating whether doses are mixed together or separate
            :return: array of floats of molecular masses, 2H first, 18O second.  Both numbers will be the same in
                        the case of a mixed dose
        """

        if mixed_dose:
            mol_mass = 2 * ((1 - dose_enrichments[0]) * 1 + dose_enrichments[0] * 2) + (
                    (1 - dose_enrichments[1]) * 16 + dose_enrichments[1] * 18)
            mol_masses = [mol_mass, mol_mass]
        else:
            mol_mass_d = 2 * ((1 - dose_enrichments[0]) * 1 + dose_enrichments[0] * 2) + (
                    (1 - O18_VSMOW_RATIO) * 16 + O18_VSMOW_RATIO * 18)
            mol_mass_o = 2 * ((1 - D_VSMOW_RATIO) * 1 + D_VSMOW_RATIO * 2) + (
                    (1 - dose_enrichments[1]) * 16 + dose_enrichments[1] * 18)
            mol_masses = [mol_mass_d, mol_mass_o]

        return mol_masses

    def calculate_various_nd(self):
        """Calculate the various dilution spaces for nd.
            :return: dict of dilution spaces for deuterium
        """

        nd = {}
        nd['plat_a_mol'] = self.dilution_space_plateau(self.dose_weights[0], self.mol_masses[0],
                                                         self.dose_enrichments[0], self.d_ratios[1], self.d_ratios[0])
        nd['plat_b_mol'] = self.dilution_space_plateau(self.dose_weights[0], self.mol_masses[0],
                                                         self.dose_enrichments[0], self.d_ratios[2], self.d_ratios[0])
        nd['plat_avg_mol'] = (nd['plat_a_mol'] + nd['plat_b_mol']) / 2

        dosetime = timedelta.total_seconds(self.sample_datetimes[2] - self.sample_datetimes[1]) / 3600
        nd['int_a_mol'] = self.dilution_space_intercept(self.dose_weights[0], self.mol_masses[0],
                                                          self.dose_enrichments[0], self.d_ratios[1], self.d_ratios[0],
                                                          self.kd_per_hr, dosetime)
        dosetime = timedelta.total_seconds(self.sample_datetimes[3] - self.sample_datetimes[1]) / 3600
        nd['int_b_mol'] = self.dilution_space_intercept(self.dose_weights[0], self.mol_masses[0],
                                                          self.dose_enrichments[0], self.d_ratios[2], self.d_ratios[0],
                                                          self.kd_per_hr, dosetime)
        nd['int_avg_mol'] = (nd['int_a_mol'] + nd['int_b_mol']) / 2

        nd['adj_plat_avg_mol'] = self.adj_dilution_space(nd['plat_avg_mol'], self.subject_weights)
        nd['adj_int_avg_mol'] = self.adj_dilution_space(nd['int_avg_mol'], self.subject_weights)
        nd['adj_plat_avg_kg'] = nd['adj_plat_avg_mol'] * STANDARD_WATER_MOL_MASS
        nd['adj_int_avg_kg'] = nd['adj_int_avg_mol'] * STANDARD_WATER_MOL_MASS
        return nd

    def calculate_various_no(self):
        """Calculate the various dilution spaces for nd.
            :return: dict of dilution spaces for deuterium
        """

        no = {}
        no['plat_a_mol'] = self.dilution_space_plateau(self.dose_weights[1], self.mol_masses[1],
                                                         self.dose_enrichments[1], self.o18_ratios[1],
                                                         self.o18_ratios[0])
        no['plat_b_mol'] = self.dilution_space_plateau(self.dose_weights[1], self.mol_masses[1],
                                                         self.dose_enrichments[1], self.o18_ratios[2],
                                                         self.o18_ratios[0])
        no['plat_avg_mol'] = (no['plat_a_mol'] + no['plat_b_mol']) / 2

        dosetime = timedelta.total_seconds(self.sample_datetimes[2] - self.sample_datetimes[1]) / 3600
        no['int_a_mol'] = self.dilution_space_intercept(self.dose_weights[1], self.mol_masses[1],
                                                          self.dose_enrichments[1], self.o18_ratios[1],
                                                          self.o18_ratios[0], self.ko_per_hr, dosetime)
        dosetime = timedelta.total_seconds(self.sample_datetimes[3] - self.sample_datetimes[1]) / 3600
        no['int_b_mol'] = self.dilution_space_intercept(self.dose_weights[1], self.mol_masses[1],
                                                          self.dose_enrichments[1], self.o18_ratios[2],
                                                          self.o18_ratios[0], self.ko_per_hr, dosetime)
        no['int_avg_mol'] = (no['int_a_mol'] + no['int_b_mol']) / 2

        no['adj_plat_avg_mol'] = self.adj_dilution_space(no['plat_avg_mol'], self.subject_weights)
        no['adj_int_avg_mol'] = self.adj_dilution_space(no['int_avg_mol'], self.subject_weights)
        no['adj_plat_avg_kg'] = no['adj_plat_avg_mol'] * STANDARD_WATER_MOL_MASS
        no['adj_int_avg_kg'] = no['adj_int_avg_mol'] * STANDARD_WATER_MOL_MASS
        return no

    @staticmethod
    def dilution_space_plateau(doseweight, molmass, doseenrichment, plateauenrichment, background):
        """Calculate a dilution space using the plateau method.
           :param doseweight: weight of the does in grams
           :param molmass: moleular mass of the dose in grams/mol
           :param doseenrichment: enrichment of the dose in ppm
           :param plateauenrichment: enrichment of the plateau urine measurement as a ratio
           :param background: enrichment of the background urine measurement as a ratio
           :return: dilution space calculated by the plateau method in mol
        """

        return doseweight / molmass * (doseenrichment - plateauenrichment) / (plateauenrichment - background)

    @staticmethod
    def dilution_space_intercept(doseweight, molmass, doseenrichment, plateauenrichment, background,
                                 turnoverrate, dosetime):
        """Calculate a dilution space using the intercept method.
           :param doseweight: weight of the does in grams
           :param molmass: moleular mass of the dose in grams/mol
           :param doseenrichment: enrichment of the dose in ppm
           :param plateauenrichment: enrichment of the plateau urine measurement in ppm
           :param background: enrichment of the background urine measurement in ppm
           :param turnoverrate: isotope turnover rate in 1/hr
           :param dosetime: time and date of dose administration
           :return: dilution space calculated by the intercept method in mol
        """

        interceptenrichment = (plateauenrichment - background) * np.exp(dosetime * turnoverrate) + background

        return doseweight / molmass * (doseenrichment - interceptenrichment) / (interceptenrichment - background)

    def avg_intercept_dilution_space(self, doseweight, molmass, doseenrichment, turnoverrate, ratios, sampledatetime):
        """Calculate the average of the 4 and 5 hour dilution spaces calculated by the intercept method
           :param doseweight: weight of the does in grams
           :param molmass: moleular mass of the dose in grams/mol
           :param doseenrichment: enrichment of the dose in ppm
           :param turnoverrate: isotope turnover rate in 1/hr
           :param ratios: measured urine isotope ratios
           :param sampledatetime: time and date of urine collections
           :return: average of the 4 and 5 hour dilution spaces calculated by the intercept method in mol
        """
        dilspace = np.zeros(2)
        dosetime = np.zeros(2)

        dosetime[0] = timedelta.total_seconds(sampledatetime[1] - sampledatetime[0]) / 3600
        dilspace[0] = self.dilution_space_intercept(doseweight, molmass, doseenrichment, ratios[1], ratios[0],
                                                    turnoverrate, dosetime[0])

        dosetime[1] = timedelta.total_seconds(sampledatetime[2] - sampledatetime[0]) / 3600
        dilspace[1] = self.dilution_space_intercept(doseweight, molmass, doseenrichment, ratios[2], ratios[0],
                                                    turnoverrate, dosetime[1])
        return np.mean(dilspace)

    @staticmethod
    def adj_dilution_space(dilution_space, subject_weights):
        """Adjust the given dilution space by the beginning and end subject weights to produce an average dilution space.
           :param dilution_space: unadjusted dilution space
           :param subject_weights: array containing before and after subject weights
           :return adj_dilution_space: dilution space in mol adjusted for the subject weight change over the
                                       sampling period
        """
        begin_dilution_spacekg = dilution_space * STANDARD_WATER_MOL_MASS
        end_dilution_spacekg = subject_weights[1] / subject_weights[0] * begin_dilution_spacekg

        adj_dilution_space = ((begin_dilution_spacekg + end_dilution_spacekg) / 2) / STANDARD_WATER_MOL_MASS
        return adj_dilution_space

    def calculate_schoeller(self):
        """Calculate the various rCO2 and TEE values using the equation of Schoeller (equation A6, 1986 as updated
            in 1988)
            :return dict of co2 and tee values from the Schoeller equation
        """
        schoeller = {}
        schoeller['co2_int'] = self.calc_schoeller_co2(self.nd['adj_int_avg_mol'], self.no['adj_int_avg_mol'],
                                                         self.kd_per_hr, self.ko_per_hr)
        schoeller['co2_plat'] = self.calc_schoeller_co2(self.nd['adj_plat_avg_mol'], self.no['adj_plat_avg_mol'],
                                                          self.kd_per_hr, self.ko_per_hr)
        schoeller = self.change_units_co2(schoeller)
        schoeller = self.tee_calcs(schoeller)

        return schoeller

    @staticmethod
    def calc_schoeller_co2(nd, no, kd, ko):
        """Calculate CO2 production in mol/hr using the equation of Schoeller (equation A6, 1986 as updated in 1988)
                from dilution spaces and isotope turnover rates.
           :param nd: deuterium dilution space in mol
           :param no: oxygen dilution space in mol
           :param kd: deuterium turnover rate in 1/hr
           :param ko: oxygen turnover rate in 1/hr
           :return co2prod: co2 production rate in mol/hr
        """
        n = ((no / 1.01) + (nd / 1.04)) / 2
        co2_prod = (n / 2.078) * (1.01 * ko - 1.04 * kd) - 0.0246 * n * 1.05 * (1.01 * ko - 1.04 * kd)
        # reduces to co2prod = n*(0.459952*ko_per_hr - 0.47362*kd_per_hr)
        return co2_prod

    def calculate_racette(self):
        """Calculate the various rCO2 and TEE values using the equation of Racette (1994)
            :return dict of co2 and tee values from the Racette equation
        """
        racette = {}
        racette['co2_int'] = self.calc_racette_co2(self.nd['adj_int_avg_mol'], self.no['adj_int_avg_mol'],
                                                         self.kd_per_hr, self.ko_per_hr, self.pop_avg_rdil)
        racette['co2_plat'] = self.calc_racette_co2(self.nd['adj_plat_avg_mol'], self.no['adj_plat_avg_mol'],
                                                          self.kd_per_hr, self.ko_per_hr, self.pop_avg_rdil)
        racette = self.change_units_co2(racette)
        racette = self.tee_calcs(racette)

        return racette

    @staticmethod
    def calc_racette_co2(nd, no, kd, ko, pop_avg_rdil):
        """Calculate CO2 production in mol/hr using the equation of Racette (1994)
                from dilution spaces and isotope turnover rates.
           :param nd: deuterium dilution space in mol
           :param no: oxygen dilution space in mol
           :param kd: deuterium turnover rate in 1/hr
           :param ko: oxygen turnover rate in 1/hr
           :return co2prod: co2 production rate in mol/hr
        """
        r_dil = (pop_avg_rdil+1.034)/2
        n = ((no / 1.01) + (nd / (1.01 *r_dil))) / 2
        co2_prod = (n / 2.078) * (1.01 * ko - 1.01 * kd * r_dil) - 0.0245 * n * 1.05 * (1.01 * ko - 1.01 * kd * r_dil)
        return co2_prod

    def calculate_speakman(self):
        """Calculate the various rCO2 and TEE values using the equation of Speakman eqn 17.41 (1997)
            :return dict of co2 and tee values from the Speakman equation
        """
        speakman = {}
        speakman['co2_int'] = self.calc_speakman_co2(self.nd['adj_int_avg_mol'], self.no['adj_int_avg_mol'],
                                                   self.kd_per_hr, self.ko_per_hr, self.pop_avg_rdil)
        speakman['co2_plat'] = self.calc_speakman_co2(self.nd['adj_plat_avg_mol'], self.no['adj_plat_avg_mol'],
                                                    self.kd_per_hr, self.ko_per_hr, self.pop_avg_rdil)
        speakman = self.change_units_co2(speakman)
        speakman = self.tee_calcs(speakman)

        return speakman

    @staticmethod
    def calc_speakman_co2(nd, no, kd, ko, pop_avg_rdil):
        """Calculate CO2 production in mol/hr using the equation of Speakman eqn 17.41 (1997)
                from dilution spaces and isotope turnover rates.
           :param nd: deuterium dilution space in mol
           :param no: oxygen dilution space in mol
           :param kd: deuterium turnover rate in 1/hr
           :param ko: oxygen turnover rate in 1/hr
           :return co2prod: co2 production rate in mol/hr
        """
        n = (no + (nd / pop_avg_rdil)) / 2
        co2_prod = (n / 2.078) * (ko - kd * pop_avg_rdil) - (0.0062 * n  * kd * pop_avg_rdil)
        return co2_prod

    @staticmethod
    def change_units_co2(equation):
        """Change the units on the co2 calculations.
            :param equation: dict with 'co2_int' and 'co2_plat' already calculated in mol/hr
            :return equation: dict now containing co2 in other units
        """

        equation['co2_int_mol_day'] = equation['co2_int'] * HOURS_PER_DAY  # rco2 mols/day
        equation['co2_int_L_hr'] = equation['co2_int'] * LITERS_PER_MOL
        equation['co2_int_L_day'] = equation['co2_int_L_hr'] * HOURS_PER_DAY  # rco2 l/day

        equation['co2_plat_mol_day'] = equation['co2_plat'] * HOURS_PER_DAY
        equation['co2_plat_L_hr'] = equation['co2_plat'] * LITERS_PER_MOL
        equation['co2_plat_L_day'] = equation['co2_plat_L_hr'] * HOURS_PER_DAY

        return equation

    @staticmethod
    def co2_to_tee(co2):
        """Convert CO2 production to total energy expenditure in using the equation of Weir, J.B. J Physiol., 109(1-2):1-9, 1949
           :param co2: volume of co2 production in mol/hr
           :return: total energy expenditure in kcal/day
        """
        return co2 * LITERS_PER_MOL * HOURS_PER_DAY * WEIR_CONSTANT

    def tee_calcs (self, equation):
        """Change the units on the tee calculations.
           :param equation: dict with co2 previously calculated
           :return equation: dict now containing tee measurements
        """

        equation['tee_int_kcal_day'] = self.co2_to_tee(equation['co2_int'])
        equation['tee_plat_kcal_day'] = self.co2_to_tee(equation['co2_plat'])

        equation['tee_int_mj_day'] = equation['tee_int_kcal_day'] * MJ_PER_KCAL
        equation['tee_plat_mj_day'] = equation['tee_plat_kcal_day'] * MJ_PER_KCAL

        return equation

    @staticmethod
    def percent_difference(first, second):
        """Calculate the percent difference between two values """
        return ((first - second) / ((first + second) / 2) * 100)

    def ee_consistency_check(self):
        """Calculate the percentage difference between the energy expenditure measured using the PD4/ED4 pair and
            the PD5/ED5 pair
            :return: percentage differences
        """
        elapsedhours = (timedelta.total_seconds(self.sample_datetimes[4] - self.sample_datetimes[2])) / 3600
        kd_a = self.isotope_turnover_2pt(self.d_ratios[0], self.d_ratios[1], self.d_ratios[3], elapsedhours)
        ko_a = self.isotope_turnover_2pt(self.o18_ratios[0], self.o18_ratios[1], self.o18_ratios[3], elapsedhours)

        elapsedhours = (timedelta.total_seconds(self.sample_datetimes[5] - self.sample_datetimes[3])) / 3600
        kd_b = self.isotope_turnover_2pt(self.d_ratios[0], self.d_ratios[2], self.d_ratios[4], elapsedhours)
        ko_b = self.isotope_turnover_2pt(self.o18_ratios[0], self.o18_ratios[2], self.o18_ratios[4], elapsedhours)

        schoeller_a = self.calc_schoeller_co2(self.nd['int_a_mol'], self.no['int_a_mol'], kd_a, ko_a)
        schoeller_b = self.calc_schoeller_co2(self.nd['int_b_mol'], self.no['int_b_mol'], kd_b, ko_b)

        tee_a = self.co2_to_tee(schoeller_a)
        tee_b = self.co2_to_tee(schoeller_b)

        diff = self.percent_difference(tee_a, tee_b)
        return diff

    def save_results_csv(self, filename):
        """ Save the results to a csv file
            :param: filename(string), the name of the file to which to save
        """
        write_header = ('subject_id,kd_hr,ko_hr,Nd_plat_avg_mol,No_plat_avg_mol, TBW_avg_kg,FFM_kg,FM_kg,body_fat_%,'
                        'sch_rCO2_int_mol/day,sch_rCO2_int_L/day,sch_EE_int_kcal/day,sch_EE_int_MJ/day,'
                        'sch_rCO2_plat_mol/day,sch_rCO2_plat_L/day,sch_EE_plat_kcal/day,sch_EE_plat_MJ/day,'
                        'rac_rCO2_int_mol/day,rac_rCO2_int_L/day,rac_EE_int_kcal/day,rac_EE_int_MJ/day,'
                        'rac_rCO2_plat_mol/day,rac_rCO2_plat_L/day,rac_EE_plat_kcal/day,rac_EE_plat_MJ/day,'
                        'spk_rCO2_int_mol/day,spk_rCO2_int_L/day,spk_EE_int_kcal/day,spk_EE_int_MJ/day,'
                        'spk_rCO2_plat_mol/day,spk_rCO2_plat_L/day,spk_EE_plat_kcal/day,spk_EE_plat_MJ/day,'
                        '2H_plateau_%,18O_plateau_%,DS_ratio,EE_consistency_check,ko/kd')
        write_data = np.asarray(
            [[self.subject_id, self.kd_per_hr, self.ko_per_hr, self.nd['plat_avg_mol'], self.no['plat_avg_mol'],
              self.total_body_water_ave_kg, self.fat_free_mass_kg, self.fat_mass_kg, self.body_fat_percent,
              self.schoeller['co2_int_mol_day'], self.schoeller['co2_int_L_day'], self.schoeller['tee_int_kcal_day'],
              self.schoeller['tee_int_mj_day'], self.schoeller['co2_plat_mol_day'], self.schoeller['co2_plat_L_hr'],
              self.schoeller['tee_plat_kcal_day'], self.schoeller['tee_plat_mj_day'],
              self.racette['co2_int_mol_day'], self.racette['co2_int_L_day'], self.racette['tee_int_kcal_day'],
              self.racette['tee_int_mj_day'], self.racette['co2_plat_mol_day'], self.racette['co2_plat_L_hr'],
              self.racette['tee_plat_kcal_day'], self.racette['tee_plat_mj_day'],
              self.speakman['co2_int_mol_day'], self.speakman['co2_int_L_day'], self.speakman['tee_int_kcal_day'],
              self.speakman['tee_int_mj_day'], self.speakman['co2_plat_mol_day'], self.speakman['co2_plat_L_hr'],
              self.speakman['tee_plat_kcal_day'], self.speakman['tee_plat_mj_day'], self.d_ratio_percent,
              self.o18_ratio_percent, self.dil_space_ratio, self.ee_check, self.ko_kd_ratio]])
        if os.path.isfile(filename):  # if the file already exists, don't rewrite the header
            file = open(filename, 'a+')
            np.savetxt(file, write_data, delimiter=',', comments='', fmt="%s")
        else:
            file = open(filename, 'a+')
            np.savetxt(file, write_data, delimiter=',', header=write_header, comments='', fmt="%s")
        file.close()
        return os.path.abspath(filename)
