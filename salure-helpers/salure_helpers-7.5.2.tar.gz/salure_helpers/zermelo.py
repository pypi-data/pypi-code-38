import requests
import traceback
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize
import datetime
import json
import time


class Zermelo():
    # For documentation see: https://wartburg.zportal.nl/static/swagger/ & https://zermelo.atlassian.net/wiki/display/DEV/API+Entities
    def __init__(self, customer, token, storage_location, initial_zermelo_extract=False, cancelled_appointments='&cancelled=false'):
        """
        Extracts data from source based on the entered parameters
        :param customer: indicates the customer
        :param token: gives access to customer data
        :param storage_location: indicates the location where the extracted data file is saved
        :param initial_zermelo_extract: store the extract as a delta file (true) or not (false)
        :param cancelled_appointments: doesn't get the cancelled appointments by default. Can be changed to an empty string to get the cancelled appointments
        """
        api_version = 3
        self.url = 'https://{0}.zportal.nl/api/v{1}/'.format(customer, api_version)
        self.access_token = token
        self.storage_location = storage_location
        self.initial_zermelo_extract = initial_zermelo_extract
        self.cancelled_appointments = cancelled_appointments

    def run_all_extracts(self):
        self.get_zermelo_appointments(endpoint='appointments', fields=['id', 'start', 'end', 'type', 'remark', 'valid', 'cancelled', 'modified',
                                                                       'moved', 'changeDescription', 'branch', 'branchOfSchool', 'created', 'lastModified',
                                                                       'hidden', 'appointmentInstance', 'new', 'teachers', 'students', 'subjects', 'groups',
                                                                       'locations', 'locationsOfBranch', 'groupsInDepartments'])
        self.get_zermelo(endpoint='branches', fields=['code', 'name'])
        self.get_zermelo(endpoint='branchesofschools', fields=['id', 'schoolInSchoolYear', 'branch', 'name'])
        self.get_zermelo(endpoint='choosableindepartments', fields=['id', 'subject', 'departmentOfBranch', 'departmentOfBranchCode', 'sectionOfBranch', 'clockHoursPerLesson', 'teachingLevelManually',
                                 'teachingLevel', 'subjectType', 'subjectCode', 'subjectName', 'scheduleCode', 'subjectScheduleCode', 'lessonDemand', 'lessonHoursInClassPeriods'],
                         nested=True, nested_fields=['lessonHoursInClassPeriods'])
        self.get_zermelo(endpoint='classperiods', fields=['id', 'name', 'schoolInSchoolYear', 'weeks'], nested=True, nested_fields=['weeks'])
        self.get_zermelo(endpoint='contracts', fields=['id', 'start', 'end', 'employee', 'defaultFunctionCategory', 'teacherTeam', 'clockHoursGeneralTasks', 'clockHoursGeneralTasksManually',
                                                       'clockHoursTasks', 'clockHoursProfessionalDevelopmentManually', 'clockHoursProfessionalDevelopment', 'clockHoursNet', 'lessonsMax', 'type',
                                                       'yearFraction', 'fteYearLeave', 'ftePermanent', 'fteTemporary', 'fteNet', 'clockHoursGross', 'clockHoursBalance', 'clockHoursLessonsMax',
                                                       'lessonReducingTasks', 'taskSpace', 'taskBalance', 'lessonSpace', 'mainBranchOfSchool', 'school', 'schoolName', 'schoolYear', 'firstName',
                                                       'lastName', 'prefix', 'clockHoursLessons'])
        self.get_zermelo(endpoint='departmentsofbranches', fields=['id', 'code', 'yearOfEducation', 'branchOfSchool', 'clockHoursPerLesson', 'schoolInSchoolYearId', 'schoolInSchoolYearName', 'studentCount', 'prognosticStudentCount'])
        self.get_zermelo(endpoint='employees', fields=['userCode', 'commencementTeaching', 'commencementSchool', 'prefix', 'gender', 'dateOfBirth', 'firstName', 'lastName', 'street', 'houseNumber', 'postalCode', 'city'])
        self.get_zermelo(endpoint='groups', fields=['id', 'code'])
        self.get_zermelo(endpoint='groupindepartments', fields=['id', 'departmentOfBranch', 'name', 'isMainGroup', 'isMentorGroup', 'extendedName'])
        self.get_zermelo(endpoint='holidays', fields=['id', 'schoolInSchoolYear', 'name', 'start', 'end'])
        self.get_zermelo(endpoint='jobs', fields=['id', 'contract', 'functionCategory', 'employmentType', 'start', 'end', 'fteReal', 'fteManually', 'fte', 'type', 'employee', 'clockHoursGross'])
        self.get_zermelo(endpoint='jobextensions', fields=['id', 'contract', 'start', 'end', 'fteReal', 'lessonsAndTasks', 'total', 'employee', 'fte', 'generalTasks', 'professionalDevelopment', 'personalBudget'])
        self.get_zermelo(endpoint='leaves', fields=['id', 'contract', 'leaveType', 'leaveTypeName', 'start', 'end', 'total', 'leaveApproved', 'employee', 'fteReal'])
        self.get_zermelo(endpoint='leavetypes', fields=['id', 'name', 'fixed', 'affectsPersonalBudget'])
        self.get_zermelo(endpoint='locations', fields=['code'])
        self.get_zermelo(endpoint='locationofbranches', fields=['id', 'name', 'parentteachernightCapacity', 'courseCapacity', 'branchOfSchool'])
        self.get_zermelo(endpoint='plannedlessons', fields=['id', 'clockHoursPerLesson', 'plannedGroups', 'lessonDemand', 'branchOfSchool', 'departmentOfBranches',
                                                            'lessonHoursInClassPeriods', 'subjects', 'sectionOfBranches', 'maxTeachingLevel', 'regularTeachingAssignments'],
                         nested=True, nested_fields=['plannedGroups', 'departmentOfBranches', 'subjects', 'sectionOfBranches', 'regularTeachingAssignments', 'lessonHoursInClassPeriods'])
        self.get_zermelo(endpoint='plannedgroups', fields=['id', 'choosableInDepartment', 'groupInDepartment', 'teachingLevel', 'subjectCode', 'groupInDepartmentName',
                                                           'groupInDepartmentIsMainGroup', 'groupInDepartmentIsMentorGroup', 'groupInDepartmentExtendedName', 'name', 'rank'])
        self.get_zermelo(endpoint='schools', fields=['id', 'name', 'brin'])
        self.get_zermelo(endpoint='schoolsinschoolyears', fields=['id', 'school', 'year', 'project', 'archived', 'projectName', 'schoolName', 'name'])
        self.get_zermelo(endpoint='sectionassignments', fields=['contract', 'id', 'lessonHoursFirstDegree', 'lessonHoursSecondDegree', 'sectionOfBranch'])
        self.get_zermelo(endpoint='selectedsubjects', fields=['id', 'subjectSelection', 'choosableInDepartment', 'alternativeChoosableInDepartment', 'manualLessonInvolvement',
                                                              'exemption', 'studentInDepartment', 'subjectCode', 'subject', 'segmentCode', 'lessonInvolvement'])
        self.get_zermelo(endpoint='sections', fields=['id', 'abbreviation', 'name', 'sectionOfBranches'], nested=True, nested_fields=['sectionOfBranches'])
        self.get_zermelo(endpoint='students', fields=['dateOfBirth', 'email', 'street', 'houseNumber', 'postalCode', 'city', 'lastName', 'prefix',
                                                     'firstName', 'lwoo', 'userCode', 'studentInDepartments'], nested=True, nested_fields=['studentInDepartments'])
        self.get_zermelo(endpoint='studentsindepartments', fields=['id', 'student', 'departmentOfBranch', 'groupInDepartments', 'mainGroup'])
        self.get_zermelo(endpoint='subjectselections', fields=['id', 'selectedSubjects', 'studentCode', 'departmentOfBranch'])
        self.get_zermelo(endpoint='subjectselectionsubjects', fields=['id', 'code', 'name', 'scheduleCode'])
        self.get_zermelo_substituded_lessons(endpoint='substitutedlessons', fields=['contract', 'employee', 'appointment', 'start', 'end', 'changeDescription', 'appointmentInstance'])
        self.get_zermelo(endpoint='taskassignments', fields=['branchOfSchool', 'contract', 'employee', 'contract', 'hours', 'hoursReplacement', 'taskGroup', 'taskInBranchOfSchool',
                                                             'type', 'start', 'end'])
        self.get_zermelo(endpoint='tasks', fields=['abbreviation', 'id', 'name', 'taskGroup', 'taskGroupAbbreviation'])
        self.get_zermelo(endpoint='taskgroups', fields=['abbreviation', 'description', 'id', 'name'])
        self.get_zermelo(endpoint='tasksinbranchofschool', fields=['branchOfSchool', 'clockHoursAssigned', 'clockHoursBalance', 'id', 'maxHours', 'task', 'taskAbbreviation'])
        self.get_zermelo(endpoint='teacherteams', fields=['id', 'name', 'branchOfSchool', 'departmentOfBranches'], nested=True, nested_fields=['departmentOfBranches'])
        self.get_zermelo(endpoint='teachingassignments', fields=['id', 'contract', 'plannedLesson', 'type', 'regular', 'lessonHoursInClassPeriodsManually', 'startWeek', 'endWeek',
                                                                 'employee', 'regularContract', 'teachingQualificationStatus', 'lessonHoursInClassPeriods', 'plannedGroups', 'lessonHoursNet'],
                         nested=True, nested_fields=['lessonHoursInClassPeriods', 'plannedGroups'])
        self.get_zermelo(endpoint='teachingqualifications', fields=['id', 'employee', 'choosable', 'startWeek', 'endWeek', 'diploma', 'teachingLevel', 'choosableAbbreviation', 'status', 'name'])
        self.get_zermelo(endpoint='workforceparameters', fields=['defaultclockhoursperlesson', 'id', 'schoolInSchoolYear'])

    def get_zermelo(self, endpoint, fields, nested=False, nested_fields=[]):
        """
        Database in Zermelo is divided in different endpoints which consist of fields. Some fields are nested, which
        means that some data lines have a subdivision.
        :param endpoint: name of the endpoint. Not case-sensitive
        :param fields: make a selection of the desired fields. Selection of the field(s) is case-sensitive
        :param nested: field is nested or not
        :param nested_fields: select nested fields
        :return: returns error when extract didn't succeed
        """
        url_fields = ','.join(fields)
        url = '{0}{1}?access_token={2}&fields={3}'.format(self.url, endpoint, self.access_token, url_fields)

        if nested:
            # Get the response without any transformation
            response = requests.get(url).json()['response']['data']

            # From all the fields, hold only the meta_fields (the not nested fields)
            meta_fields = fields.copy()
            for nested_field in nested_fields:
                meta_fields.remove(nested_field)

            # From the initial response, create a dataframe with only the meta_fields
            df = pd.DataFrame(response)
            df = df[meta_fields]

            # Set the columns in df as the same type as in the original df. Sometimes, an empty field will change the column type in df_temp
            # to object while the dtype in the original df is int or float. This will give an error when merging
            existing_field_types = dict(df.dtypes)
            for column in df:
                if column in existing_field_types:
                    existing_dtype = existing_field_types[column]
                    if existing_dtype == 'int64' or existing_dtype == 'float64':
                        df[column] = df[column].fillna(0)
                        df[column] = df[column].astype(existing_dtype)

            # Loop through the nested_fields, create a dataframe for each nested field and join the result to the initial dataframe
            for nested_field in nested_fields:
                # If the nested_field hold a key, value pair, then the record_prefix is usable. Only a value give a TypeError. Catch this error and rename the column
                try:
                    df_temp = pd.io.json.json_normalize(data=response, meta=meta_fields, record_path=[nested_field], record_prefix='{}_'.format(nested_field))
                except TypeError:
                    df_temp = pd.io.json.json_normalize(data=response, meta=meta_fields, record_path=[nested_field])
                    df_temp.rename(columns={0: nested_field}, inplace=True)
                # Set the columns in df_temp as the same type as in the original df. Sometimes, an empty field will change the column type in df_temp
                # to object while the dtype in the original df is int or float. This will give an error when merging
                existing_field_types = dict(df.dtypes)
                for column in df_temp:
                    if column in existing_field_types:
                        existing_dtype = existing_field_types[column]
                        if existing_dtype == 'int64' or existing_dtype == 'float64':
                            df_temp[column] = df_temp[column].fillna(0)
                            df_temp[column] = df_temp[column].astype(existing_dtype)
                # Merge the initial dataframe and the new one
                df = pd.merge(df, df_temp, how='left', on=meta_fields)
            data = df
        else:
            init_response = json.loads(requests.get(url).content)
            status = init_response['response']['status']
            if status == 200:
                data = pd.DataFrame(init_response['response']['data'])

                # Check each column if the column only holds integers. If yes, and the type is a Float, set type to float. Otherwise, this gives problems in QLik Sense (2 becomes 2.0)
                for column in data.columns:
                    try:
                        if data.loc[:, column].dtype == np.float64 or data.loc[:, column].dtype == np.int64:
                            data.loc[:, column].fillna(0, inplace=True)
                        else:
                            data.loc[:, column].fillna('', inplace=True)
                        column_name = 'check_{}'.format(column)
                        data.loc[:, column_name] = data.apply(lambda x: 'int64' if x[column].is_integer() else 'float', axis = 1)
                        if 'float' in data.loc[:, column_name].values:
                            pass
                        else:
                            data.loc[:, column] = data.loc[:, column].astype('int64')
                        del data[column_name]
                    except Exception as e:
                        continue

            else:
                data = init_response['response']['message']
                print(data)

        data.index.name = '{0}_id'.format(endpoint)
        file = '{0}{1}.csv'.format(self.storage_location, endpoint)
        data.to_csv(file, '|')
        print('{0} - {1} saved'.format(time.strftime('%H:%M:%S'), endpoint))

    def get_zermelo_substituded_lessons(self, endpoint, fields):
        start = time.time()
        fields = ','.join(fields)

        if datetime.datetime.today().month <= 7:
            if self.initial_zermelo_extract:
                start_of_data = datetime.date(year=(datetime.datetime.today().year - 6), month=9, day=1).timetuple()
            else:
                start_of_data = datetime.date(year=(datetime.datetime.today().year - 1), month=9, day=1).timetuple()
        else:
            start_of_data = datetime.date(year=datetime.datetime.today().year, month=9, day=1).timetuple()

        # Loop through the data per week (3600 seconds * 24 hours * 7 days) because the dataset is to big to receive in once. Start three years back
        df = pd.DataFrame()

        start_epoch = int(time.mktime(start_of_data))
        now_epoch = time.mktime(datetime.datetime.today().timetuple())
        while start_epoch < now_epoch:
            try:
                if (start_epoch +  (3600 * 24 * 7)) > now_epoch:
                    end_epoch = int(now_epoch)
                else:
                    end_epoch = int(start_epoch +  (3600 * 24 * 7))

                print(start_epoch, end_epoch)
                url = '{0}{1}?access_token={2}&fields={3}&start={4}&end={5}'.format(self.url, endpoint, self.access_token, fields, start_epoch, end_epoch)
                data = requests.get(url).json()['response']['data']

                # checks if data is not empty list
                if data:
                    df_new = pd.DataFrame(data)
                    df_new['changeDescription'] = df_new['changeDescription'].str.replace('\n', '')
                    df_new['changeDescription'] = df_new['changeDescription'].str.replace('\r', '')
                    df = pd.concat([df, df_new])

                start_epoch += (3600 * 24 * 7)

            except Exception as e:
                print('{} - Error at timestamp {}: {}'.format(time.strftime('%H:%M:%S'), start_epoch, e))

        # Store the total dataframe to a new csv file
        df.drop_duplicates(inplace=True)
        df.reset_index(drop=True, inplace=True)
        df.index.name = '{0}_id'.format(endpoint)
        file = '{0}{1}.csv'.format(self.storage_location, 'substituded_lessons')
        df.to_csv(file, '|')

        print('Done in {} seconds'.format(time.time() - start))

    def get_zermelo_appointments(self, endpoint, fields):
        start = time.time()
        fields = ','.join(fields)

        if datetime.datetime.today().month <= 7:
            if self.initial_zermelo_extract:
                start_of_data = datetime.date(year=(datetime.datetime.today().year - 6), month=9, day=1).timetuple()
            else:
                start_of_data = datetime.date(year=(datetime.datetime.today().year - 1), month=9, day=1).timetuple()
        else:
            start_of_data = datetime.date(year=datetime.datetime.today().year, month=9, day=1).timetuple()

        # Loop through the data per week (3600 seconds * 24 hours * 7 days) because the dataset is too big to receive in once. Start three years back
        df = pd.DataFrame()

        start_epoch = int(time.mktime(start_of_data))
        now_epoch = time.mktime(datetime.datetime.today().timetuple())
        while start_epoch < now_epoch:
            try:
                if (start_epoch +  (3600 * 24 * 2)) > now_epoch:
                    end_epoch = int(now_epoch)
                else:
                    end_epoch = int(start_epoch +  (3600 * 24 * 2))
                print(start_epoch, end_epoch)
                url = '{0}{1}?access_token={2}&fields={3}&start={4}&end={5}&includeHidden=True{6}&valid=True'.format(self.url, endpoint, self.access_token, fields, start_epoch, end_epoch, self.cancelled_appointments)
                data = requests.get(url).json()['response']['data']

                # checks if data is not empty list
                if data:
                    df_new = pd.DataFrame(data)
                    df_new['remark'] = df_new['remark'].str.replace('\n', '')
                    df_new['remark'] = df_new['remark'].str.replace('\r', '')

                    df = pd.concat([df, df_new])
                # Add one week
                start_epoch += (3600 * 24 * 2)

            except Exception as e:
                print('{} - Error at timestamp {}: {}'.format(time.strftime('%H:%M:%S'), start_epoch, e))

        # Reset some columns from Float to Int
        df.loc[:, 'branchOfSchool'].fillna(0, inplace=True)
        df.loc[:, 'branchOfSchool'] = df.loc[:, 'branchOfSchool'].astype('int64')
        df.reset_index(inplace=True, drop=True)

        # Subtract all the nested layers from the appointments and save to separate files
        self.appointments_create_lookup_table(df, 'students', 'userCode')
        self.appointments_create_lookup_table(df, 'teachers', 'userCode')
        self.appointments_create_lookup_table(df, 'subjects', 'scheduleCode')
        self.appointments_create_lookup_table(df, 'groups', 'code')
        self.appointments_create_lookup_table(df, 'locations', 'code')
        self.appointments_create_lookup_table(df, 'locationsOfBranch', 'id')
        self.appointments_create_lookup_table(df, 'groupsInDepartments', 'id')

        # Store the total dataframe to a new csv file
        df.drop(columns=['students', 'teachers', 'subjects', 'groups', 'locations', 'locationsOfBranch', 'groupsInDepartments'], inplace=True)
        df.index.name = '{0}_id'.format(endpoint)
        file = '{0}{1}.csv'.format(self.storage_location, 'appointments')
        df.to_csv(file, '|')
        print('Done in {} seconds'.format(time.time() - start))

    def appointments_create_lookup_table(self, df, col_name, link_id):
        df = df[['id', col_name]]
        # Only hold rows whith filled arrays
        df = df[df[col_name].apply(len) > 0]
        appointments_lookup_df = []
        for index, row in df.iterrows():
            appointmentId = row['id']
            to_link = row[col_name]
            for item in to_link:
                appointments_lookup_df.append({'appointmentsId': appointmentId, link_id: item})
        df = pd.DataFrame(appointments_lookup_df)
        file = '{0}{1}.csv'.format(self.storage_location, 'appointments_{0}'.format(col_name))
        df.index.name = 'appointments_{0}_id'.format(col_name)
        df.to_csv(file, '|')
