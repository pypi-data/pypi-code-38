import csv
import os
import re
import json
import shutil
import subprocess
import nbformat
import sys
import urllib.request
import warnings
import itertools

import matplotlib.pyplot as plt
from notebook import notebookapp
import nbconvert
import nbgrader
from nbconvert.preprocessors import CellExecutionError, ExecutePreprocessor
import numpy as np
import pandas as pd
import seaborn as sns
from bs4 import BeautifulSoup
from canvasapi import Canvas
from collections import defaultdict, Counter
from IPython.display import Javascript, Markdown, display, clear_output
from ipywidgets import (Button, Layout, fixed, interact, interact_manual,
                        interactive, widgets)
from nbgrader.apps import NbGraderAPI
from tqdm import tqdm, tqdm_notebook  # Progress bar
from traitlets.config import Config
warnings.filterwarnings('ignore')


class Course:
    canvas_course = None
    filename = 'workflow.json'

    resits = {}
    groups = {}
    sequence = []
    requirements = []

    def __init__(self):
        if self.filename in os.listdir():
            self.load_pickle()
        else:
            self.gradedict = {}
        if self.canvas_course is None:
            if "key" not in self.__dict__.keys() or "url" not in self.__dict__.keys(
            ) or "canvas_id" not in self.__dict__.keys():
                change_canvas_credentials()
            else:
                self.log_in(self.canvas_id, self.url, self.key)

        config = Config()
        config.Exchange.course_id = os.getcwd().split('\\')[-1]
        self.nbgrader_api = NbGraderAPI(config=config)
        
    def change_canvas_credentials(self, canvas_id='',url="https://canvas.uva.nl", key=''):
        if "key" in self.__dict__.keys():
            key=self.key
        if "url" in self.__dict__.keys():
            url=self.url
        if "canvas_id" in self.__dict__.keys():
            canvas_id=self.canvas_id
        login_button = interact_manual.options(
                    manual_name="Log in to Canvas")
        login_button(
            self.log_in,
            canvas_id=canvas_id,
            url=url,
            key=key)
        
    def show_course_settings(self):
        endlist = []
        enddict = defaultdict(list)
        for k,v in self.resits.items():
            if type(v)==list:
                for a in v:
                    enddict[a].append(k)
            elif type(v)==str:
                enddict[v].append(k)

        for k,v in self.groups.items():
            weight = round(v["weight"]/ len(v["assignments"]),2)
            for a in v["assignments"]:
                if a in self.sequence:
                    index = self.sequence.index(a)
                else:
                    index = np.nan
                if a in enddict:
                    resits = [x for x in self.sequence if x in enddict[a]]
                else:
                    resits = np.nan
                if a in self.gradedict:
                    min_grade = self.gradedict[a]['min_grade']
                    max_score = self.gradedict[a]['max_score']
                else:
                    if a in (x.name for x in self.nbgrader_api.gradebook.assignments):
                        min_grade = 0
                        max_score = self.nbgrader_api.gradebook.find_assignment(a).max_score
                    else:
                        min_grade = np.nan
                        max_score = np.nan
                endlist.append([k,a,index,resits, weight, min_grade, max_score])

        for a in self.resits:
            if a in self.gradedict:
                min_grade = self.gradedict[a]['min_grade']
                max_score = self.gradedict[a]['max_score']
            else:
                if a in (x.name for x in self.nbgrader_api.gradebook.assignments):
                    min_grade = 0
                    max_score = self.nbgrader_api.gradebook.find_assignment(a).max_score
                else:
                    min_grade = np.nan
                    max_score = np.nan

            if a in self.sequence:
                index = self.sequence.index(a)
            else:
                index = np.nan
            if a in enddict:
                resits = enddict[a]
            else:
                resits = np.nan
            endlist.append(["Resits",a, index,resits, np.nan, min_grade, max_score])

        df = pd.DataFrame(endlist,columns = ["Group", "Assignment","Order","Resits", "Weight","Minimal Grade","Points needed for a 10"])
        display(df.set_index(["Group","Assignment"]))
        print("To pass a course a student has to")
        for r in self.requirements:
            if type(r["groups"]) == str:
                print("\thave a minimal mean grade of {:.1f} for {}".format(r["min_grade"],r["groups"]))
            elif type(r["groups"]) == list:
                if len(r["groups"]) == 1:
                    print("\thave a minimal mean grade of {:.1f} for {}".format(r["min_grade"],r["groups"]))
                elif len(r["groups"]) > 1:
                    print("\thave a minimal mean grade of {:.1f} for {} and {}".format(r["min_grade"],", ".join(r["groups"][:-1]), r["groups"][-1]))
        print("\thave a minimal weighted mean grade of 5.5 for all groups")

        

    def log_in(self, canvas_id, url, key):
        try:
            canvas_obj = Canvas(url, key)
            self.canvas_course = canvas_obj.get_course(int(canvas_id))
            self.canvas_id = canvas_id
            self.url = url
            self.key = key
            self.save_pickle()

            print("Logged in succesfully")
            print("Course name: %s\nCourse code: %s" %(self.canvas_course.name,self.canvas_course.course_code))
            print("Canvas course id: %s" %canvas_id)
            print("Username: %s" %(canvas_obj.get_current_user().name))
            change_login_button = Button(
                        description="Change course/user",
                        layout=Layout(width='300px'))
            change_login_button.on_click(self.change_canvas_credentials)
            display(change_login_button)
        except ValueError:
            print("Course id should be an integer")
            self.change_canvas_credentials()
        except InvalidAccessToken:
            print("Incorrect key")
            change_canvas_credentials()


    def load_pickle(self):
        f = open(self.filename, 'r')
        tmp_dict = json.load(f)
        f.close()

        self.__dict__.update(tmp_dict)

    def save_pickle(self):
        f = open(self.filename, 'w')
        temp = {
            k: v for k,
            v in self.__dict__.items() if type(v) in [
                str,
                list,
                dict,
                int,
                float]}
        json.dump(temp, f, indent=4, sort_keys=True)
        f.close()

    def button_db(self):
        db_button = Button(
            description="Update the students in the database",
            layout=Layout(width='300px'))
        db_button.on_click(self.update_db)
        return db_button

    def update_db(self, b):
        assert self.canvas_course is not None
        if self.canvas_course is None:
            print("This only works if connected to Canvas")
            return
        for student in tqdm_notebook(
                self.canvas_course.get_users(enrollment_type=['student'])):
            first_name, last_name = student.name.split(' ', 1)

            self.nbgrader_api.gradebook.update_or_create_student(
                str(student.sis_user_id),
                first_name=first_name,
                last_name=last_name)

    def assign_button(self):
        interact_assign = interact_manual.options(
            manual_name="Assign assignment")

        return interact_assign(
            self.assign, assignment_id=self.nbgrader_assignments(), run_to_check_for_errors=False)

    def assign(self, assignment_id, run_to_check_for_errors):
        file = 'source/' + assignment_id + '/' + assignment_id + ".ipynb"
        assert os.path.exists(
            file), "The folder name and notebook name are not equal."
        subprocess.run(["nbgrader", "update", file])
        subprocess.run([
            "nbgrader", "assign", assignment_id, "--create", "--force"])
        if run_to_check_for_errors:
            with open("nbgrader_config.py") as f:
                contents = f.read()
                timer = 30
                if "ExecutePreprocessor.timeout" in contents:
                    timer=min(int(x) for x in re.findall(r'ExecutePreprocessor\.timeout\s*=\s*(\d*)', contents))
            ep = ExecutePreprocessor(timeout=timer, kernel_name='python3')
            with open(file,encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
                try:
                    out = ep.preprocess(nb,{'metadata': {'path': 'source/%s/' %assignment_id}})
                except CellExecutionError:
                    out = None
                    msg = 'Error executing the notebook "%s".\n' % file
                    msg += 'See notebook for the traceback.'
                    print(msg)
                except TimeoutError:
                    msg = "Timeout (after %s seconds) in on of the cells\n" %timer
                    msg += 'Consider changing the timeout in nbgrader_config.py'
                    print(msg)
                finally:
                    with open(file, mode='w', encoding='utf-8') as f:
                        nbformat.write(nb, f)

        if self.canvas_course is not None:
            assignmentdict = {
                assignment.name: assignment.id
                for assignment in self.canvas_course.get_assignments()
            }

            # If Assignment does not exist, create assignment
            if assignment_id not in assignmentdict.keys():
                self.canvas_course.create_assignment(
                    assignment={
                        'name': assignment_id,
                        'points_possible': 10,
                        'submission_types': 'online_upload',
                        'allowed_extensions': 'ipynb',
                        'published': 'True'
                    })

    def nbgrader_assignments(self):
        return sorted([
            assignment
            for assignment in self.nbgrader_api.get_source_assignments()
        ])

    def download_button(self):
        interact_download = interact_manual.options(
            manual_name="Download files")
        return interact_download(
            self.download_files, assignment_id=self.nbgrader_assignments())

    def download_files(self, assignment_id):
        if self.canvas_course is not None:
            if assignment_id in [
                    assignment.name
                    for assignment in self.canvas_course.get_assignments()
            ]:
                # Get sis id's from students
                student_dict = self.get_student_ids()

                # Get the Canvas assignment id
                assignment = self.get_assignment_obj(assignment_id)
                groups = []

                for submission in tqdm_notebook(
                    assignment.get_submissions(
                        include=['group'])):
                    if submission.group['id'] is not None:
                        if submission.group['id'] in groups:
                            continue
                        else:
                            groups.append(submission.group['id'])
                    # Check if submission has attachments
                    if 'attachments' not in submission.attributes:
                        continue
                    # Download file and give correct name
                    student_id = student_dict[submission.user_id]
                    attachment = submission.attributes["attachments"][0]

                    directory = "submitted/%s/%s/" % (student_id,
                                                      assignment_id)
                    if not os.path.exists(directory):
                        os.makedirs(directory)

                    filename = assignment_id + ".ipynb"
                    urllib.request.urlretrieve(attachment['url'],
                                               directory + filename)
                    # Clear all notebooks of output to save memory
                    subprocess.run(["nbstripout", directory + filename])
        else:
            print("No assignment found on Canvas")
        # Move the download files to submission folder
        if os.path.exists('downloaded/%s/' % (assignment_id)):
            for file in os.listdir('downloaded/%s/' % (assignment_id)):
                pass
            subprocess.run([
                "nbgrader", "zip_collect", assignment_id, "--force",
                "--log-level='INFO'"
            ])

    def get_assignment_obj(self, assignment_name):
        return {
            assignment.name: assignment
            for assignment in self.canvas_course.get_assignments()
        }[assignment_name]

    def autograde_button(self):
        interact_autograde = interact_manual.options(manual_name="Autograde")
        return interact_autograde(
            self.autograde, assignment_id=self.nbgrader_assignments())

    def autograde(self, assignment_id):
        pbar = tqdm_notebook(
            sorted(
                self.nbgrader_api.get_submitted_students(assignment_id)))
        for student in pbar:
            pbar.set_description("Currently grading: %s" % student)
            student2 = "'" + student + "'"
            subprocess.run([
                "nbgrader", "autograde", assignment_id, "--create", "--force",
                "--student=%s" % student2
            ])
        localhost_url = [x['url'] for x in notebookapp.list_running_servers(
        ) if x["notebook_dir"] == os.getcwd()][0]
        display(
            Markdown(
                '<a class="btn btn-primary" style="margin-top: 10px; text-decoration: none;" href="%sformgrader/gradebook/%s/%s" target="_blank">Klik hier om te manual graden</a>' %
                (localhost_url, assignment_id, assignment_id)))

    def plagiat_button(self):
        interact_plagiat = interact_manual.options(
            manual_name="Check for plagiarism")
        return interact_plagiat(
            self.plagiarism_check,
            assignment_id=self.nbgrader_assignments())

    def plagiarism_check(self, assignment_id):
        if os.path.exists('plagiarismcheck/%s/' % assignment_id):
            shutil.rmtree(
                'plagiarismcheck/%s/' % assignment_id, ignore_errors=True)
        os.makedirs('plagiarismcheck/%s/pyfiles/' % assignment_id)
        os.makedirs('plagiarismcheck/%s/base/' % assignment_id)

        test = nbconvert.PythonExporter()
        test2 = test.from_filename(
            'release/%s/%s.ipynb' % (assignment_id, assignment_id))
        f = open(
            "plagiarismcheck/%s/base/%s.py" % (assignment_id, assignment_id),
            "w", encoding="utf-8")
        f.write(test2[0])
        f.close()

        for folder in tqdm_notebook(
                self.nbgrader_api.get_submitted_students(assignment_id),
                desc='Converting notebooks to .py'):
            test2 = test.from_filename('submitted/%s/%s/%s.ipynb' %
                                       (folder, assignment_id, assignment_id))
            f = open(
                "plagiarismcheck/%s/pyfiles/%s_%s.py" %
                (assignment_id, folder, assignment_id), "w", encoding="utf-8")
            f.write(test2[0])
            f.close()
        os.makedirs("plagiarismcheck/%s/html/" % assignment_id)
        try:
            subprocess.run(["compare50", "plagiarismcheck/%s/pyfiles/*" %
                            assignment_id, "-d", "plagiarismcheck/%s/base/*" %
                            assignment_id, "-o", "plagiarismcheck/%s/html/" %
                            assignment_id], shell=True)
        except BaseException:
            print(
                "Install check50 for plagiarism check. (This is not available on Windows)")
        display(
            Markdown(
                '<a class="btn btn-primary" style="margin-top: 10px; text-decoration: none;" href="plagiarismcheck/%s/" target="_blank">Open folder with results of plagiarism check/a>' %
                assignment_id))

    def color_grades(self, row):
        if row['interval'].right <= 5.5:
            return 'r'
        else:
            return 'g'

    def grades_button(self):
        return interact(
            self.interact_grades, assignment_id=self.graded_submissions())

    def visualize_grades(self, assignment_id, min_grade, max_score):
        """Creates a plot of the grades from a specific assignment"""
        grades = self.create_grades_per_assignment(assignment_id, min_grade,
                                                   max_score)[assignment_id]
        index = (i["student"]
                 for i in self.nbgrader_api.get_submissions(assignment_id)
                 if i["autograded"])

        grades = grades.reindex(index, axis='index').dropna()
        print("The mean grade is {:.1f}".format(grades.mean()))
        print("The median grade is {}".format(grades.median()))
        print("Maximum of Cohen-Schotanus is {:.1f}".format(
            grades.nlargest(max(1, int(len(grades) * 0.05))).mean()))
        print("The percentage insufficent grades is {:.1f}%. ".format(
            100 * sum(grades < 5.5) / len(grades)))
        sns.set(style="darkgrid")
        bins = np.arange(1, 10, 0.5)
        interval = [pd.Interval(x, x + 0.5, closed='left') for x in bins]
        interval[-1] = pd.Interval(left=9.5, right=10.001, closed='left')
        interval = pd.IntervalIndex(interval)
        new_grades = grades.groupby([pd.cut(grades, interval)]).size()
        test_grades = pd.DataFrame(new_grades)
        test_grades.columns = ["Test"]
        test_grades = test_grades.reset_index()
        test_grades.columns = ["interval", "Test"]
        test_grades['color'] = test_grades.apply(self.color_grades, axis=1)
        fig, ax = plt.subplots()
        ax.set_xlim(1, 10)
        ax.xaxis.set_ticks(range(1, 11))
        ax2 = ax.twinx()
        ax2.yaxis.set_ticks([])
        ax.bar(
            bins,
            new_grades,
            width=0.5,
            align="edge",
            color=test_grades['color'])
        sns.kdeplot(grades, ax=ax2, clip=(1, 10), legend=False)

        grades_button = Button(
            description="Save grades", layout=Layout(width='300px'))
        grades_button.on_click(self.update_grades)
        self.curr_assignment = assignment_id
        self.curr_grade_settings = {
            "max_score": max_score,
            "min_grade": min_grade
        }
        display(grades_button)

    def item_button(self):
        return interact(
            self.question_visualizations,
            assignment_id=self.graded_submissions())

    def update_grades(self, b):
        self.gradedict[self.curr_assignment] = self.curr_grade_settings
        self.save_pickle()

    def p_value(self, df):
        return df.groupby(
            'question_name', sort=False)['final_score'].mean() / df.groupby(
                'question_name', sort=False)['max_score'].mean()

    def create_grades_per_assignment(self,
                                     assignment_name,
                                     min_grade=None,
                                     max_score=None):
        canvasdf = pd.DataFrame(
            self.nbgrader_api.gradebook.submission_dicts(
                assignment_name)).set_index('student')
        if min_grade is None and max_score is None:
            min_grade, max_score, _= self.get_default_grade(
                assignment_name)

        canvasdf['grade'] = canvasdf['score'].apply(
            lambda row: self.calculate_grade(row, min_grade, max_score))
        canvasdf = canvasdf.pivot_table(
            values='grade', index='student', columns='name', aggfunc='first')
        return canvasdf

    def total_df(self):
        list_of_dfs = [
            self.create_grades_per_assignment(x)
            for x in self.graded_submissions()]
        if list_of_dfs==[]:
            return None
        canvasdf = pd.concat(list_of_dfs,
                             axis=1)
        return canvasdf

    def calculate_grade(self, score, min_grade, max_score):
        """Calculate grade for an assignment"""
        return max(
            1,
            min(
                round(min_grade + (10 - min_grade) * score / max_score, 1),
                10.0))

    def graded_submissions(self):
        return [
            x['name'] for x in self.nbgrader_api.get_assignments()
            if x['num_submissions'] > 0
        ]

    def create_results_per_question(self):
        q = '''
            SELECT
                submitted_assignment.student_id,
                grade_cell.name AS question_name,
                grade_cell.max_score,
                grade.needs_manual_grade AS needs_grading,
                grade.auto_score,
                grade.manual_score,
                grade.extra_credit,
                assignment.name AS assignment
            FROM grade
                INNER JOIN submitted_notebook ON submitted_notebook.id = grade.notebook_id
                INNER JOIN submitted_assignment ON submitted_assignment.id = submitted_notebook.assignment_id
                INNER JOIN grade_cell ON grade_cell.id = grade.cell_id
                INNER JOIN assignment ON submitted_assignment.assignment_id = assignment.id
        '''

        df = pd.read_sql_query(q, 'sqlite:///gradebook.db')

        df['final_score'] = np.where(
            ~pd.isnull(df['manual_score']), df['manual_score'],
            df['auto_score']) + df['extra_credit'].fillna(0)
        return df.fillna(0)

    def interact_grades(self, assignment_id):
        score_list = self.get_default_grade(assignment_id)
        if score_list is None:
            print("No grades in the database")
            return
        min_grade, max_score, abs_max = score_list
        interact(
            self.visualize_grades,
            assignment_id=fixed(assignment_id),
            min_grade=widgets.FloatSlider(
                value=min_grade,
                min=0,
                max=9.5,
                step=0.5,
                continuous_update=False),
            max_score=widgets.FloatSlider(
                value=max_score,
                min=0.5,
                max=abs_max,
                step=0.5,
                continuous_update=False))

    def get_default_grade(self, assignment_id):
        assignment = self.nbgrader_api.gradebook.find_assignment(assignment_id)
        if assignment.num_submissions < 1:
            return None
        abs_max = assignment.max_score
        min_grade = 0
        if assignment_id in self.gradedict.keys():
            if "max_score" in self.gradedict[assignment_id].keys():
                max_score = self.gradedict[assignment_id]["max_score"]

            if "min_grade" in self.gradedict[assignment_id].keys():
                min_grade = self.gradedict[assignment_id]["min_grade"]
        else:
            max_score = abs_max

        return min_grade, max_score, abs_max

    def question_visualizations(self, assignment_id):
        df = self.create_results_per_question()
        df = df.loc[df['assignment'] == assignment_id]
        df = df[df['max_score'] > 0]
        if df.empty:
            print('DataFrame is empty')
            return
        p_df = self.p_value(df)
        rir_df = self.create_rir(df)
        combined_df = pd.concat([p_df, rir_df], axis=1)
        combined_df = combined_df.reindex(list(p_df.index))
        combined_df = combined_df.reset_index()
        combined_df.columns = ["Question", "P value", "Rir value", "positive"]

        sns.set(style="darkgrid")
        fig, axes = plt.subplots(1, 2, figsize=(12, 7), sharey=True)
        plt.suptitle('P value and Rir value per question')
        sns.barplot(
            x="P value", y="Question", data=combined_df, color='b',
            ax=axes[0]).set_xlim(0, 1.0)
        sns.barplot(
            x="Rir value",
            y="Question",
            data=combined_df,
            ax=axes[1],
            palette=combined_df["positive"]).set_xlim(-1.0, 1.0)

    def f(self, row):
        if row['Rir-waarde'] <= 0:
            return 'r'
        elif row['Rir-waarde'] <= 0.25:
            return 'y'
        else:
            return 'g'

    def create_rir(self, df):
        testdict = {}

        if len(df["student_id"].unique()) < 50:
            print("Norm of 50 students not reached to be meaningful")

        df["total_score_item"] = df["extra_credit"] + df["auto_score"] + df[
            "manual_score"]
        df['student_score-item'] = df['total_score_item'].groupby(
            df['student_id']).transform('sum') - df['total_score_item']
        for question in sorted(set(df["question_name"].values)):
            temp_df = df.loc[df['question_name'] == question]
            testdict[question] = temp_df[[
                "total_score_item", "student_score-item"
            ]].corr().iloc[1, 0]
        testdf = pd.DataFrame.from_dict(
            testdict, orient='index', columns=["Rir-waarde"])
        testdf['positive'] = testdf.apply(self.f, axis=1)
        return testdf

    def replace_with_resits(self, df, resit_name):
        assignments = self.resits[resit_name]
        if isinstance(assignments, list):
            for v1 in assignments:
                df[v1] = np.where(
                    df[resit_name].isnull(), df[v1], df[resit_name])
        else:
            df[assignments] = np.where(
                df[resit_name].isnull(),
                df[assignments],
                df[resit_name])
        return df

    def create_overview(self, df):
        if self.canvas_course is None:
            if df is None:
                return None
            df.dropna(1, how='all', inplace=True)
            df = df.fillna(0)
        else:
            canvas_df = self.create_canvas_grades_df()
            canvas_df.dropna(1, how='all', inplace=True)
            if canvas_df.empty or canvas_df.sum().sum()==0:
                return None
            for column in df.dropna(1, how='all').columns:
                if column not in canvas_df.columns:
                    canvas_df = canvas_df.join(df[column].fillna(0), how='left')
                
            df = canvas_df

        l = [x for x in self.sequence if x in df.columns]
        testlist = []

        for n, c in enumerate(l):
            if c in self.resits.keys():
                df = self.replace_with_resits(df, c)

            onvoldoendes = []
            for requirement in self.requirements:
                if isinstance(requirement["groups"], list):

                    assignments = set()
                    for group_name in requirement["groups"]:
                        assignments |= set(
                            self.groups[group_name]["assignments"])
                    weighted_total = self.add_total_to_df(
                        df[assignments & set(l[:n + 1])])[0]
                    
                    onvoldoendes += list(weighted_total[weighted_total
                                            < requirement["min_grade"]].index)

                else:
                    columns = set(
                        [x for x in l[:n + 1] if x in self.groups[requirement["groups"]]["assignments"]])
                    if columns != set():
                        onvoldoendes += list(df[df[columns].mean(axis=1)
                                                < requirement["min_grade"]].index)

            weighted_total = self.add_total_to_df(df[l[:n + 1]])[0]
            onvoldoendes += list(weighted_total[weighted_total < 5.5].index)

            fail_counter = Counter(Counter(onvoldoendes).values())
            temp_df = df[df[c] > 0]
            did_not_participate = (set(df.index) -
                                   set(temp_df.index)) & set(onvoldoendes)
            fail_counter = Counter(
                Counter([x for x in onvoldoendes if x not in did_not_participate]).values())
            testlist.append([c, len(df) - len(set(onvoldoendes))] + [fail_counter[x]
                                                                     for x in range(1, len(self.requirements) + 2,)] + [len(did_not_participate)])

        testdf = pd.DataFrame(
            testlist,
            columns=[
                "Assignment Name",
                "Pass",
                "Insuifficient for 1 requirement"] +
            [
                "Insuifficient for %i requirements" %
                i for i in range(
                    2,
                    len(
                        self.requirements) +
                    2)] +
            ["Did not participate in this assignment &\n insuifficient for requirement(s)"]).set_index("Assignment Name")
        return testdf

    def visualize_overview(self):
        df = self.total_df()
        overviewdf = self.create_overview(df)
        if df is None:
            print("No grades available")
            return None

        fig, axes = plt.subplots(2, 1, figsize=(12, 12), sharex=True)
        sns.set(style="darkgrid")
        plt.suptitle('Overview of the course', y=0.93)
        df = df.reindex([x for x in self.sequence if x in overviewdf.index], axis=1)
        a = sns.boxplot(data=df.mask(df < 1.0), ax=axes[0])
        a.set_title('Boxplot for each assignment')
        a.set_ylim(1, 10)
        sns.despine()
        flatui = sns.color_palette("Greens",
                                   1) + sns.color_palette("YlOrRd",
                                                          len(overviewdf.columns) - 2) + sns.color_palette("Greys",
                                                                                                           1)
        sns.set_palette(flatui)
        b = overviewdf.plot.bar(
            stacked=True,
            color=flatui,
            ylim=(0, overviewdf.sum(axis=1).max()),
            width=1.0,
            legend='reverse',
            ax=axes[1])
        b.set_title(
            'How many students have suifficient grades to pass after that assignment'
        )
        plt.xticks(rotation=45)
        plt.legend(
            loc='right',
            bbox_to_anchor=(1.4, 0.8),
            fancybox=True,
            shadow=True,
            ncol=1)

    def upload_button(self):
        if self.canvas_course is None:
            print(
                "Credentials for Canvas were not provided, therefore it is not possible to upload.")
            return
        canvas_button = interact_manual.options(
            manual_name="Grades to Canvas")
        canvas_button(
            self.upload_to_canvas,
            assignment_name=self.canvas_and_nbgrader())

    def upload_to_canvas(self, assignment_name, message='', feedback=False):
        print(feedback, assignment_name, message)
        if feedback:
            subprocess.run([
                "nbgrader", "feedback", "--quiet", "--force",
                "--assignment=%s" % assignment_name
            ])

        # Haal de laatste cijfers uit gradebook
        canvasdf = self.total_df()
        student_dict = self.get_student_ids()

        assignment = self.get_assignment_obj(assignment_name)
        # Check if assignment is published on Canvas, otherwise publish
        if not assignment.published:
            assignment.edit(assignment={"published": True})
        # loop over alle submissions voor een assignment, alleen als er
        # attachments zijn
        for submission in tqdm_notebook(
                assignment.get_submissions(), desc='Submissions', leave=False):
            try:
                student_id = student_dict[submission.user_id]
            except Exception as e:
                continue
            if student_id not in list(canvasdf.index.values):
                continue
            grade = canvasdf.at[student_id, assignment_name]
            if np.isnan(grade):
                continue
            # alleen de cijfers veranderen als die op canvas lager zijn of niet
            # bestaan
            if submission.attributes[
                    'score'] != grade and submission.attributes['score'] != 0:
                if feedback:
                    feedbackfile = create_feedback(student_id, assignment_name)
                    submission.upload_comment(feedbackfile)
                submission.edit(
                    submission={'posted_grade': str(grade)},
                    comment={'text_comment': message})

        # Delete feedbackfiles to save memory
        if 'canvasfeedback' in os.listdir():
            shutil.rmtree('canvasfeedback/', ignore_errors=True)
        if 'feedback' in os.listdir():
            shutil.rmtree('feedback/', ignore_errors=True)

    def get_student_ids(self):
        return {
            student.id: student.sis_user_id
            for student in self.canvas_course.get_users()
        }

    def visualize_validity(self):
        canvas_grades = self.total_df()
        if canvas_grades is None:
            print("No grades available")
            return
        cronbach_df = self.cronbach_alpha_plot()
        fig, axes = plt.subplots(1, 2, figsize=(15, 7))
        sns.set(style="darkgrid")
        a = sns.heatmap(
            canvas_grades.corr(),
            vmin=-1,
            vmax=1.0,
            annot=True,
            linewidths=.5,
            cmap="RdYlGn",
            ax=axes[0])
        a.set_title("Correlations between assignments")
        a.set(ylabel='', xlabel='')

        b = sns.barplot(
            y="Assignment",
            x="Cronbachs Alpha",
            data=cronbach_df,
            palette=map(self.color_ca_plot, cronbach_df["Cronbachs Alpha"]),
            ax=axes[1])
        b.set_xlim(0, 1.0)
        b.set(ylabel='')
        b.set_title("Cronbachs Alpha for each assignment")

    def create_feedback(self, student_id, assignment_id):
        """Given a student_id and assignment_id, creates a feedback file without the Hidden Tests"""
        directory = 'feedback/%s/%s/' % (student_id, assignment_id)
        soup = str(
            BeautifulSoup(
                open(
                    "%s%s.html" % (directory, assignment_id),
                    encoding='utf-8'), "html.parser"))
        css, html = soup.split('</head>', 1)
        html = re.sub(
            r'(<div class="output_subarea output_text output_error">\n<pre>\n)(?:(?!<\/div>)[\w\W])*(<span class="ansi-red-intense-fg ansi-bold">[\w\W]*?<\/pre>)',
            r'\1\2',
            html)
        html = re.sub(
            r'<span class="c1">### BEGIN HIDDEN TESTS<\/span>[\w\W]*?<span class="c1">### END HIDDEN TESTS<\/span>',
            '',
            html)
        soup = css + '</head>' + html
        targetdirectory = 'canvasfeedback/%s/%s/' % (student_id, assignment_id)
        if not os.path.exists(targetdirectory):
            os.makedirs(targetdirectory)
        filename = "%s%s.html" % (targetdirectory, assignment_id)
        Html_file = open(filename, "w", encoding="utf8")
        Html_file.write(soup)
        Html_file.close()
        return filename

    def color_ca_plot(self, c):
        pal = sns.color_palette("RdYlGn_r", 6)
        if c >= 0.8:
            return pal[0]
        elif c >= 0.6:
            return pal[1]
        else:
            return pal[5]

    def cronbach_alpha_plot(self):
        testlist = []
        df = pd.pivot_table(
            self.create_results_per_question(),
            values='final_score',
            index=['student_id'],
            columns=['assignment', 'question_name'],
            aggfunc=np.sum)

        for assignment_id in sorted(set(df.columns.get_level_values(0))):
            items = df[assignment_id].dropna(how='all').fillna(0)

            # source:
            # https://github.com/anthropedia/tci-stats/blob/master/tcistats/__init__.py
            items_count = items.shape[1]
            variance_sum = float(items.var(axis=0, ddof=1).sum())
            total_var = float(items.sum(axis=1).var(ddof=1))

            testlist.append((assignment_id,
                             (items_count / float(items_count - 1) *
                              (1 - variance_sum / total_var))))

        cronbach_df = pd.DataFrame(
            testlist, columns=["Assignment", "Cronbachs Alpha"])
        return cronbach_df

    def canvas_and_nbgrader(self):
        canvas = set(assignment.name
                     for assignment in self.canvas_course.get_assignments())
        nbgrader = set(
            assignment
            for assignment in self.nbgrader_api.get_source_assignments())
        return sorted(canvas & nbgrader)

    def TurnToUvaScores(self, s):
        # 5.5 can't exist
        if s > 5 and s < 6:
            return round(s)

        # Because rounding is weird in python
        # https://stackoverflow.com/questions/14249971/why-is-pythons-round-so-strange
        elif int(2 * s) % 2 == 0:
            return 0.5 * (round(2 * s + 1) - 1)
        else:
            return 0.5 * round(2 * s)

    def NAV(self, row, dict_of_weights):
        if row.Totaal < 5.5:
            return "NAV"

        for requirement in self.requirements:
            if isinstance(requirement["groups"], list):
                total_weight = sum([dict_of_weights[group]
                                    for group in requirement["groups"]])
                total = sum([row[group] * dict_of_weights[group]
                             for group in requirement["groups"]])
                if total / total_weight < requirement["min_grade"]:
                    return "NAV"
            else:
                if row[requirement["groups"]] < requirement["min_grade"]:
                    return "NAV"

        return row.Totaal

    def add_total_to_df(self, df):
        dict_of_weights = {}
        assignment_dict = [l for l in self.canvas_course.get_assignments()]
        for group_name, d in self.groups.items():
            if len(set(d["assignments"]) & set(df.columns)) > 0:
                dict_of_weights[group_name] = d['weight']
                assignments = [
                    l.name for l in assignment_dict
                    if l.name in d['assignments']
                ]
                df[group_name] = df[set(df.columns) & set(
                    assignments)].fillna(0).mean(axis=1)

        dict_of_weights = {
            x: y / sum(dict_of_weights.values())
            for x, y in dict_of_weights.items()}
        df["Totaal"] = 0
        for k, v in dict_of_weights.items():
            df["Totaal"] += df[k] * v
        return df["Totaal"], dict_of_weights

    def create_canvas_grades_df(self):
        student_dict = self.get_student_ids()

        assignment_list = [l for l in self.canvas_course.get_assignments()]
        dict_of_grades = {
            i.name: {
                student_dict[j.user_id]: j.grade
                for j in i.get_submissions() if j.user_id in student_dict
            }
            for i in assignment_list
        }

        return pd.DataFrame.from_dict(
            dict_of_grades, orient='columns').astype(float)

    def final_grades(self):
        if self.canvas_course is None:
            print("This function only works with Canvas.")
            return
        df = self.create_canvas_grades_df()
        if df.empty:
            print("No grades available")
            return
        resits = [
            assignment for assignment in self.sequence if assignment in self.resits.keys()]
        for resit in resits:
            df = self.replace_with_resits(df, resit)
        df.dropna(1, how='all', inplace=True)

        df["Totaal"], dict_of_weights = self.add_total_to_df(df)

        df["Totaal"] = df["Totaal"].map(self.TurnToUvaScores)
        df["TotaalNAV"] = df.apply(
            lambda row: self.NAV(
                row, dict_of_weights), axis=1)
        df["TotaalNAV"].reset_index().to_csv(
            'final_grades.csv', header=[
                "Student", "Final_grade"], index=False)
        df["cat"] = df.TotaalNAV != 'NAV'
        df["Passed"] = np.where(df.cat, df.Totaal, np.nan)
        df["Failed"] = np.where(df.cat, np.nan, df.Totaal)

        ax = df[["Passed", "Failed"]].plot.hist(
            bins=np.arange(-0.25, 10.5, 0.5), colors=['green', 'red'], title="Final grades")
        ax.set_xlim(xmin=0, xmax=10)
        ax.set_xticks(np.arange(0, 10.5, 1))
        print("Grades have been exported to final_grades.csv")
        if set(self.canvas_and_nbgrader()).issuperset(set(
                itertools.chain.from_iterable(v["assignments"] for k, v in self.groups.items()))):
            final_grades_button = interact_manual.options(
                manual_name="Upload final grades")
            final_grades_button(
                self.upload_final_grades,
                column="", totalnav=fixed(df["TotaalNAV"]))

    def upload_final_grades(self, column, totalnav):
        assignmentdict = {
            assignment.name: assignment.id
            for assignment in self.canvas_course.get_assignments()
        }

        # If Assignment does not exist, create assignment
        if column not in assignmentdict.keys():
            self.canvas_course.create_assignment(
                assignment={
                    'name': column,
                    'points_possible': 10,
                    'submission_types': 'online_upload',
                    'published': 'True',
                    'omit_from_final_grade': True
                })

        student_dict = self.get_student_ids()
        assignment = self.get_assignment_obj(column)
        # Check if assignment is published on Canvas, otherwise publish
        if not assignment.published:
            assignment.edit(assignment={"published": True})
        # loop over alle submissions voor een assignment, alleen als er
        # attachments zijn
        for submission in tqdm_notebook(
                assignment.get_submissions(), desc='Students', leave=False):
            try:
                student_id = student_dict[submission.user_id]
            except Exception as e:
                continue
            if student_id not in list(totalnav.index.values):
                continue
            grade = totalnav.at[student_id]
            if grade == "NAV":
                grade = 0
            if not np.isnan(grade):
                submission.edit(submission={'posted_grade': str(grade)})
