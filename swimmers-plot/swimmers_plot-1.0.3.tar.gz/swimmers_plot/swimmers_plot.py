import numpy as np
from intervaltree import Interval, IntervalTree
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages

plt.ioff()


class Cohort:
    colors = ('#A61181', '#278C18', '#67C8F3', '#F88B10', '#103129', '#5D77FE', '#98161A', '#68ECAC', '#F98E87', '#371230', '#535216', '#F72424', '#004F72', '#F34184', '#3CB9B3', '#B9B1F3', '#8B2243', '#B229BA', '#3A92E7', '#829F15', '#A15BF3', '#833D11', '#F84B51', '#204B20', '#2D6D74', '#FFA9C7', '#37B371', '#222A03', '#3879A6', '#AC3C0F', '#734CCC', '#153D49', '#43154A', '#7B5870', '#576A2E', '#25423A', '#844F3E', '#473A20', '#3B6872', '#2E6B5A', '#544449', '#5A617C', '#79424C', '#685D30', '#314352', '#475F41', '#7F552C', '#584F5C', '#DCD4C2', '#232224', '#C8DCE0', '#495145', '#E0C7CE', '#787F71', '#8E94A6', '#99A79C', '#A28B91')

    def __init__(self, patients=None):
        self.patients = patients if patients else []
        self._patient_dict = {p.patient_id:p for p in self.patients}
        self.color_dict = {}
        self.counter = 0
        self.marker_dict = {}

    def __getitem__(self, key):
        return self._patient_dict[key]

    def __repr__(self):
        return repr(self.patients)

    def add_patient(self, patient):
        """
        Add a patient
        Args:
            patient: Patient class or dict with kwargs
        """
        if isinstance(patient, Patient):
            if patient.patient_id in self._patient_dict:
                raise ValueError('Duplicate patient IDs not allowed')
            self.patients.append(patient)
            self._patient_dict[patient.patient_id] = patient
        else:
            if patient['patient_id'] in self._patient_dict:
                raise ValueError('Duplicate patient IDs not allowed')
            new_patient = Patient(cohort=self, **patient)
            self.patients.append(new_patient)
            self._patient_dict[patient['patient_id']] = new_patient

    def load_samples(self, sample_file, header=True, automark=True):
        """
        Load samples
        Args:
            sample_file: Path to sample file
                fields in order are - patient_id, label, date, marker(optional)
            header: Set to True to skip header row
            automark: Set to True if marker field is skipped
        """
        marker_list = ['o', 'x', 's', '*', '+', 'D']
        counter = 0
        with open(sample_file) as sf:
            if header:
                sf.readline()
            for line in sf:
                row = line.strip('\n').split('\t')
                patient_id = row[0]
                if patient_id not in self._patient_dict:
                    self.add_patient({'patient_id': patient_id})
                label = row[1]
                date = float(row[2])
                if automark and label not in self.marker_dict:
                    if counter>5:
                        raise ValueError('Too many unique sample groups (max: 6)')
                    marker = marker_list[counter]
                    counter += 1
                elif automark:
                    marker = self.marker_dict[label]
                else:
                    marker = row[3]
                self[patient_id].add_sample({'date': date, 'label': label, 'marker': marker})

    def load_treatments(self, treatment_file, header=True):
        """
        Load treatments
        Args:
            treatment_file: Path to treatment file
                fields in order are - patient_id, regimen, start_date, end_date
                    regimen should be treatments delimited by '/'
                    if end_date is empty or 'nan' the treatment will set as current
            header: Set to True to skip header row
        """
        with open(treatment_file) as tf:
            if header:
                tf.readline()
            for line in tf:
                row = line.strip('\n').split('\t')
                patient_id = row[0]
                if patient_id not in self._patient_dict:
                    self.add_patient({'patient_id': patient_id})
                regimen = set(row[1].split('/'))
                start_date = float(row[2])
                end_date = float(row[3]) if row[3] else np.nan
                self[patient_id].add_treatment({'regimen': regimen, 'start_date': start_date, 'end_date': end_date})

    def make_swimmers_plot(self, filename=None, figsize=(10,10), zero_at=None, sorting_key=None, linewidth=0.5):
        """
        Create a swimmers plot
        Args:
            filename: Name of output file
            figsize: (width, height) of figure
            zero_at: Name of treatment group to set start date as 0
            sorting_key: Function to determine the order patients appear
            linewidth: Width of treatment lines

        Returns:
            Axes object
        """
        plt.figure(figsize=figsize)
        ax = plt.gca()
        if sorting_key:
            temp_patients = sorted(self.patients, key=sorting_key)
        else:
            temp_patients = list(self.patients)
        max_x = 0
        min_x = 0
        y_pos = 0
        for i,patient in enumerate(temp_patients):
            treatments = patient.split_overlapping_treatments()
            zero = None
            if zero_at:
                for start, stop, regimen in treatments:
                    if zero_at in regimen:
                        zero = start
                        break
                if zero is None:
                    continue
            else:
                zero = 0
            for start, stop, regimen in treatments:
                if start-zero<min_x:
                    min_x = start-zero
                step = linewidth/len(regimen)
                if np.isnan(stop):
                    for ii,tx in enumerate(regimen):
                        adjusted_y_pos = y_pos+((linewidth/2)-(step*ii) if len(regimen)>1 else 0)
                        ax.scatter(start-zero, adjusted_y_pos, c=self.color_dict[tx], marker='>', zorder=0)
                else:
                    if stop-zero>max_x:
                        max_x = stop-zero
                    for ii,tx in enumerate(regimen):
                        adjusted_y_pos = y_pos-(linewidth/2)+(step*ii)
                        ax.fill_between([start-zero,stop-zero], [adjusted_y_pos,adjusted_y_pos],
                                        [adjusted_y_pos+step,adjusted_y_pos+step],
                                        color=self.color_dict[tx], zorder=-1, alpha=0.6)
            for date, label, marker in patient.samples:
                if date-zero<min_x:
                    min_x = date-zero
                if date-zero>max_x:
                    max_x = date-zero
                ax.scatter(date-zero, y_pos, c='black', marker=marker, zorder=1)
            y_pos -= 1
        if zero_at:
            ax.vlines(0, y_pos, 1, linewidth=1, linestyle='dashed', color='black')
        x_inc = int((max_x-min_x)//10)
        min_x = int(min_x//x_inc*x_inc-(0 if min_x%x_inc else x_inc))
        max_x = int(max_x//x_inc*x_inc+(0 if max_x%x_inc else x_inc))
        for x in range(min_x, max_x, x_inc*2):
            ax.add_patch(mpatches.Rectangle([x, y_pos], x_inc, -y_pos+2, ec='none', color='gray', alpha=0.1))
        ax.set_xlim(min_x, max_x)
        ax.set_ylim(y_pos, 1)
        ax.set_yticks(range(0, y_pos, -1))
        ax.set_yticklabels(temp_patients)
        keys = []
        labels = []
        for label, marker in self.marker_dict.items():
            keys.append(ax.scatter(0, 10, c='black', marker=marker))
            labels.append(label)
        for label, color in self.color_dict.items():
            keys.append(ax.hlines(0, 0, 0, color=color, linewidth=5, alpha=0.6))
            labels.append(label)
        ax.legend(keys, labels, bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode='expand', borderaxespad=0.,
                  frameon=False)
        if filename:
            if filename.endswith('.pdf'):
                with PdfPages(filename) as pdf:
                    pdf.savefig()
            else:
                plt.savefig(filename, bbox_inches='tight')
        return ax


class Patient:
    def __init__(self, patient_id, cohort, samples=None, treatments=None):
        self.patient_id = patient_id
        self.cohort = cohort
        self.samples = samples if samples else []
        self.treatments = treatments if treatments else []

    def __hash__(self):
        return hash((self.patient_id, id(self.cohort)))+1

    def __str__(self):
        return self.patient_id

    def __repr__(self):
        return '<Patient: {}>'.format(self.patient_id)

    def add_sample(self, sample):
        if isinstance(sample, Sample):
            self.samples.append(sample)
        else:
            self.samples.append(Sample(cohort=self.cohort, **sample))

    def add_treatment(self, treatment):
        if isinstance(treatment, Treatment):
            self.treatments.append(treatment)
        else:
            self.treatments.append(Treatment(cohort=self.cohort, **treatment))

    def split_overlapping_treatments(self):
        treatment_tree = IntervalTree()
        current_treatments = []
        for tx in self.treatments:
            if np.isnan(tx.end_date):
                current_treatments.append(tx)
            else:
                treatment_tree.add(Interval(*tx))
        treatment_tree.split_overlaps()
        treatment_tree.merge_equals(lambda a,b: a.union(b))
        return [Treatment(i.data, i.begin, i.end) for i in treatment_tree]+current_treatments


class Sample(tuple):
    def __new__(cls, date, cohort=None, label='Sample', marker='o'):
        if cohort and label not in cohort.marker_dict:
            if marker in cohort.marker_dict.values():
                raise ValueError('Markers must be unique')
            cohort.marker_dict[label] = marker
        return tuple.__new__(cls, (date, label, marker))

    def __init__(self, date, cohort=None, label='Sample', marker='o'):
        self.date = date
        self.label = label
        self.marker = marker

    def __repr__(self):
        return 'Sample({}, {})'.format(self.date, self.label)


class Treatment(tuple):
    def __new__(cls, regimen, start_date, end_date, cohort=None):
        if cohort:
            for tx in regimen:
                if tx not in cohort.color_dict:
                    if cohort.counter>56:
                        raise ValueError('Too many unique treatment groups (max: 57)')
                    cohort.color_dict[tx] = cohort.colors[cohort.counter]
                    cohort.counter += 1
        return tuple.__new__(cls, (start_date, end_date, regimen))

    def __init__(self, regimen, start_date, end_date, cohort=None):
        self.regimen = regimen
        self.start_date = start_date
        self.end_date = end_date

    def __repr__(self):
        return 'Treatment({}, {}, {})'.format('/'.join(self.regimen), self.start_date, self.end_date)
