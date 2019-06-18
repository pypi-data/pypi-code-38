from flask import Flask, render_template, request, Markup, jsonify
import os
import re
import codecs
import json
from collections import defaultdict
import glob
import nltk
import pandas as pd
from pandas import DataFrame
import numpy as np
import math

from sklearn.model_selection import train_test_split
from nltk.tokenize import RegexpTokenizer, word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from textblob import Word

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


from sklearn.naive_bayes import MultinomialNB
#import sys
#reload(sys)
#sys.setdefaultencoding('utf8')
 
app = Flask(__name__)

def jupyter_to_csv():
    data_folder = './data/'

    filenames = os.listdir(data_folder)  # get all files' and folders' names in the current directory

    student_ids = []
    for filename in filenames:  # loop through all the files and folders
        if not os.path.isdir(
                os.path.join(os.path.abspath(data_folder), filename)) and re.search("^.+ipynb$", filename):  # check whether the current object is a folder or not
            student_ids.append(filename)

    student_ids.sort()

    id_for_ans = []
    ques_num = []
    ques = []
    answers = []
    checksums = []
    
    for student_id in student_ids:
	count = 0
        with open(data_folder + student_id) as json_file: 
            source_is_ans = False
            data = json.load(json_file)
	    for (index, cell) in enumerate(data['cells']):
		if 'nbgrader' in cell['metadata'] and cell['metadata']['nbgrader']['solution'] == False \
		    and cell['metadata']['nbgrader']['grade'] == False:

		    next_cell = data['cells'][index+1]
		    if 'nbgrader' in next_cell['metadata'] and next_cell['metadata']['nbgrader']['solution'] == True:
		        count = count+1
    			current_question = "Question_"+str(count)
    			ques_num.append(current_question)
    			checksum_of_question = cell['metadata']['nbgrader']["checksum"]
    			checksums.insert(count, checksum_of_question)
			ques.append(cell['source'][2])

                        ans_source = next_cell['source']    
                        ans = ''
                        for string in ans_source:
                            ans = ans+string
                        answers.append(ans)
                        id_for_ans.append(student_id)
		    else:
			continue

#            for idx in range(len(data['cells'])):
#                p = data['cells'][idx]
#                source = p['source']

#                if len(source)>1:
#                    if "Question" in source[0]:
#                        #source_is_ans = True
#                        m = re.search('(Question.+?[0-9]*)', source[0])
#                        if m:
#                            ques_num.append(m.group(1))
#                        ques.append(p['source'][2])
#                    
#                        a = data['cells'][idx+1]
#                        ans_source = a['source']    
#                        ans = ''
#                        for string in ans_source:
#                            ans = ans+string
#                        answers.append(ans)
#                        id_for_ans.append(student_id)
    data = {'student_id': id_for_ans,
            'question_number': ques_num,
	    'checksum_of_question': checksums,
            'question': ques,
            'answers':  answers}

    df = DataFrame(data,columns= ['student_id', 'question_number', 'checksum_of_question', 'question', 'answers'])
    df.to_csv('./csv/labels/all_data.csv', encoding='utf-8')

    df1 = df.sort_values(by ='question_number' )
    df1.set_index(keys=['question_number'], drop=False,inplace=True)
    q_nums = df1['question_number'].unique().tolist()

#    all_questions = {}
    for q_num in q_nums:
	q = df1.loc[df1.question_number==q_num]
#        ques_num = q_num.split(' ')
#        ques_num = '_'.join(word for word in ques_num)
#      	 all_questions[q_num] = ques_num
        q.to_csv('./csv/'+q_num+'.csv', encoding='utf-8')
    	
    return q_nums

def read_csv(filename): 
    data = pd.read_csv(filename)
    list_corpus = data["answers"].tolist()
    list_labels = [''] * len(list_corpus)
        
    return data,list_corpus,list_labels 

def safe_strings():
    global list_corpus
    for idx in range(len(list_corpus)):
    	ans = list_corpus[idx]
	if pd.isnull(ans) or ans == "YOUR ANSWER HERE":
		ans = "NO ANSWER PROVIDED"
		list_corpus[idx] = ans
	if isinstance(ans, str):
   		list_corpus[idx] = unicode(ans, 'utf-8')
#	elif isinstance(ans, unicode):
#   		list_corpus[idx] = ans.encode('ascii', 'ignore')

def preprocess_data(X_train):
    tokenizer = RegexpTokenizer(r'[a-zA-Z]+')

    stop_words = stopwords.words('english')
    stop_words.sort()

    #stemmer = PorterStemmer()

    for i in range(len(X_train)):
        ans = X_train[i]
        words  = word_tokenize(ans)
        wordsFiltered = []
        for w in words:
            if w not in stop_words:
                wordsFiltered.append(Word(w).lemmatize())

        ans = ' '.join(word for word in wordsFiltered)
        X_train[i] = ans
    return X_train

def tfidf(X_train,X_test):
    vectorizer = TfidfVectorizer(stop_words="english", analyzer='word',ngram_range=(1, 3))
    train_vectors = vectorizer.fit_transform(X_train)
    test_vectors = vectorizer.transform(X_test)
    return vectorizer, train_vectors, test_vectors
        
def naive_bayes(train_vectors, y_train,test_vectors):
    nb = MultinomialNB(alpha=.01)
    nb.fit(train_vectors, y_train)
    y_pred = nb.predict(test_vectors)
    return nb,y_pred
    
def sorted_features(vectorizer,nb):
    #global nb
    correct_class_prob_sorted = nb.feature_log_prob_[0, :].argsort()
    incorrect_class_prob_sorted = nb.feature_log_prob_[1, :].argsort()

    correct = np.take(vectorizer.get_feature_names(), correct_class_prob_sorted[:-1])
    incorrect = np.take(vectorizer.get_feature_names(), incorrect_class_prob_sorted[:-1])
        
    return correct,incorrect

def learn():
    global X_train, X_test, y_train, y_pred, correct, incorrect
    X_train = preprocess_data(X_train)
    vectorizer, train_vectors, test_vectors = tfidf(X_train,X_test)
    nb,y_pred = naive_bayes(train_vectors,y_train,test_vectors)
    correct,incorrect = sorted_features(vectorizer,nb)

def update_phrase_exp(item,trig_tok,list_,phrase_list):
    for phrase in list_:
        phrase_tok = nltk.word_tokenize(phrase)
        tok_len = len(trig_tok)
        phrase_len = len(phrase_tok)
                   
        if tok_len == phrase_len and \
        trig_tok[0] == phrase_tok[0] and \
        item not in phrase_list:
            phrase_list.append(item)  
    return phrase_list  

def generate_explanation(test_idx):
	#TODO : modify to make case insensitiv checks
	global correct_phrases, incorrect_phrases, X_test, y_pred, correct, incorrect
        pred = y_pred[test_idx]
        tokens = nltk.word_tokenize(X_test[test_idx])

        bigram_tuples = list(nltk.bigrams(tokens))
        bigrams = []
        for a, b in bigram_tuples:
            bigram = ' '.join((a, b))
            bigrams.append(str(bigram))

        trigram_tuples = list(nltk.trigrams(tokens))
        trigrams = []
        for a, b, c in trigram_tuples:
            if c != '.':
                trigram = ' '.join((a, b, c))
            else:
                b = ''.join((b, c))
                bigram = ' '.join((a, b))
                bigrams.append(str(bigram))
            trigrams.append(str(trigram))
            

        correct_phrases = []
        incorrect_phrases = []
        #if pred == 'Correct':
        correct = map(str, correct)
        incorrect = map(str, incorrect)
        
        for item in bigrams:
            if item in correct:
                correct_phrases.append(item)
            elif item in incorrect:
                incorrect_phrases.append(item)
                
        for item in trigrams:
            if item in correct:
                correct_phrases.append(item)
            elif item in incorrect:
                incorrect_phrases.append(item)
            else:
                trig_tok = nltk.word_tokenize(item)
                if pred == 'Correct':
                    list_ = correct
                    correct_phrases = update_phrase_exp(item,trig_tok,
                                           list_,correct_phrases)
                else:
                    list_ = incorrect
                    incorrect_phrases = update_phrase_exp(item,trig_tok,
                                           list_,incorrect_phrases)
                        
                        #Also update the tfidf list
        for item in tokens:
            if item in  correct:
                correct_phrases.append(item)
            elif item in incorrect:
                incorrect_phrases.append(item)
            
        return correct_phrases,incorrect_phrases

def remove_duplicate_phrases(phrase_list):
        unigrams = []
        bigrams = []
        trigrams = []
        
        for item in phrase_list:
            tokens =  nltk.word_tokenize(item)
            length = len(tokens)
            
            if length == 2:
                bigrams.append(item)
            elif length == 3:
                trigrams.append(item)
        
        #remove duplicate unigrams in phrase list that is also in bigrams
        for bigram in bigrams:
            bigr_tokens = nltk.word_tokenize(bigram)
            for tok in bigr_tokens:
                phrase_list[:] = (value for value in phrase_list if value != tok)
                
        #remove duplicate unigrams and bigrams in phrase list that is also in trigrams    
        for trigram in trigrams:
            trig_tokens = nltk.word_tokenize(trigram)
            for trig_tok in trig_tokens:
                phrase_list[:] = (value for value in phrase_list if value != trig_tok)
                
            bigram_tuples = list(nltk.bigrams(trig_tokens))
            
            for a, b in bigram_tuples:
                bigram = ' '.join((a, b))
                bigram = str(bigram)
                phrase_list[:] = (value for value in phrase_list if value != bigram)
                
        return phrase_list

def as_html_op(x_test, y_pred,feedback=False):
	global correct_phrases, incorrect_phrases, saved_expl

	ans = x_test
        correct_mark_tags = ['<mark style="background-color:#E6EE9C;\">','</mark>']
        incorrect_mark_tags = ['<mark style="background-color:#FFAB91;\">','</mark>']

        #TODO :Mark stopwords in white
        if y_pred == 'Correct':
            for phrase in correct_phrases:
                highlighted_phrase = correct_mark_tags[0]+phrase+correct_mark_tags[1]
                x_test = x_test.replace(phrase,highlighted_phrase)
            for phrase in incorrect_phrases:
                if phrase not in correct_phrases:
                    highlighted_phrase = incorrect_mark_tags[0]+phrase+incorrect_mark_tags[1]
                    x_test = x_test.replace(phrase,highlighted_phrase)
        
        if y_pred == 'Incorrect':
            for phrase in incorrect_phrases:
                highlighted_phrase = incorrect_mark_tags[0]+phrase+incorrect_mark_tags[1]
                x_test = x_test.replace(phrase,highlighted_phrase)
            for phrase in correct_phrases:
                if phrase not in incorrect_phrases:
                    highlighted_phrase = correct_mark_tags[0]+phrase+correct_mark_tags[1]
                    x_test = x_test.replace(phrase,highlighted_phrase)

	saved_expl[ans] = x_test
        return x_test

def correction_after_feedback(feedback_corr,feedback_incorr):
	global correct_phrases, incorrect_phrases, vocab_corr, vocab_incorr
        for phrase in feedback_corr:
            if phrase not in correct_phrases:
                correct_phrases.append(phrase)
                
        for phrase in feedback_incorr:
            if phrase not in incorrect_phrases:
                incorrect_phrases.append(phrase)

#This following code is tentative       
#        for phrase in vocab_corr:
#            if phrase in incorrect_phrases:
#                incorrect_phrases.remove(phrase)
                
#        for phrase in vocab_incorr:
#            if phrase in correct_phrases:
#                correct_phrases.remove(phrase)
        return correct_phrases, incorrect_phrases

def grade_and_explain(feedback):
    global correct_phrases,incorrect_phrases,X_test,y_pred
    global html_out,pred
    global saved_grades
    #global saved_ans, given_grades, highlight_green, highlight_red


    learn()
    idx = 0
    pred = y_pred[idx]
    x_test = X_test[idx]
    correct_phrases,incorrect_phrases = generate_explanation(idx)
    correct_phrases = remove_duplicate_phrases(correct_phrases)
    incorrect_phrases = remove_duplicate_phrases(incorrect_phrases)

    #saved_ans.append(x_test)
    #given_grades.append(pred)
    
    #highlight_green.append(correct_phrases)
    #highlight_red.append(incorrect_phrases)

    saved_grades[x_test] = pred

    if feedback == 'False':         
    	html_out = Markup(as_html_op(x_test,pred))
    else:
	for phrase in vocab_corr:
	    if phrase not in correct_phrases:
	        correct_phrases.append(phrase)

    	for phrase in vocab_incorr:
	    if phrase not in incorrect_phrases:
	        incorrect_phrases.append(phrase)
	html_out = Markup(as_html_op(x_test,pred))

    return pred,html_out

def integrate_in_jupyter(output_file):

    print "Not implemented yet"

def create_output_csv():
    global data, list_corpus, saved_grades, saved_expl
    global question, ques

    id_for_ans = data['student_id'].tolist()
    ques_num = data['question_number'].tolist()
    ques = []
    answers = []
    grades_given = []
    explanations = []
    for idx in range(len(list_corpus)):
	ans = list_corpus[idx]
	ques.insert(idx, question)
	answers.insert(idx, ans)
	grades_given.insert(idx, saved_grades[ans])
	explanations.insert(idx, saved_expl[ans])

    output = {'student_id': id_for_ans,
            'question_number': ques_num,
            'question': ques,
            'answers':  answers,
            'grades_given': grades_given,
            'explanations':  explanations}

    df = DataFrame(data,columns= ['student_id', 'question_number', 'question', 'answers', 'grades_given', 'explanations'])

    if not os.path.exists('./outputs/'):
    	os.makedirs('./outputs/')
    output_file = './outputs/'+ques+'.csv'
    df.to_csv(output_file,encoding='utf-8')

    integrate_in_jupyter(output_file)

qlist  = jupyter_to_csv()
ques = qlist[0]
#ques_file = question_filenames[ques]

#questions = read_question_file()
#qlist = ['1.1','1.5','2.1','2.5','2.7','3.3','4.5','7.4','11.1','12.4','12.8','12.9','12.10']
#ques='1.1'
#question = questions[ques]
directory = 'csv/'

data,list_corpus,list_labels = read_csv(directory+ques+".csv")
#data,list_corpus,list_labels = read_csv(directory+ques_file+".csv")
questions = data["question"].unique().tolist()
question = questions[0]

X_train, X_test, y_train, y_test = train_test_split(list_corpus, list_labels, test_size=0.45,random_state=40)
selected='False'
model_ans="Model answer not provided."

stud_ans = []
for idx in range(len(X_train)):
    stud_ans.append(X_train[idx])

scores = []
vocab_corr = []
vocab_incorr = []
pred = ""
html_out = ""


#saved_ans = []
#given_grades = []
#highlight_green = []
#highlight_red = []
true_grades = []

saved_expl = {}
saved_grades = {}
end = None

@app.route('/', methods=['GET', 'POST'])
def index():
    global stud_ans
    ans=stud_ans[0]
    stud_ans.remove(ans)
    return render_template('index.html',
			   ans=ans,
			   qlist=qlist,
			   question=question,
			   model_ans=model_ans,
			   selected=selected)

@app.route('/new', methods=['GET', 'POST'])
def new():
    global stud_ans,directory,data,list_corpus,list_labels 
    global X_train, X_test, y_train, y_test, saved_expl, saved_grades
    global selected, qlist, ques, question, model_ans, question_filenames

    if request.method == "POST":
	ques = request.form['question']
	#ques_file = question_filenames[ques]
	
	filepath = directory+ques+".csv"
	data,list_corpus,list_labels = read_csv(filepath)
	safe_strings()

	questions = data["question"].unique().tolist()
	question = questions[0]

	X_train, X_test, y_train, y_test = train_test_split(list_corpus, 
							    list_labels, 
							    test_size=0.45,
							    random_state=40)
	saved_expl = {}
	saved_grades = {}
	stud_ans = []
	y_train = []
	for idx in range(len(X_train)):
    	    stud_ans.append(X_train[idx])
	#question = questions[ques]
	model_ans = "Model answer not provided."
	ans=stud_ans[0]
    	stud_ans.remove(ans)
	selected='True'
    	return render_template('index.html',ans=ans,
					    qlist=qlist,
					    ques=ques,
					    question=question,
					    model_ans=model_ans,
					    selected=selected)


@app.route("/grading", methods=['GET', 'POST'])
def grading():
    global stud_ans, scores, X_train, X_test, y_train
    global selected, qlist, ques, question, model_ans
    global saved_grades, saved_expl

    feedback = "False"
    ans = ""

    grade = request.form['grade']
    scores.append(grade)
    y_train.append(grade)
    if len(stud_ans)>0:
	ans = stud_ans[0]
	saved_expl[ans] = "Manually graded. No Explanation!!"
	saved_grades[ans] = grade

	stud_ans.remove(ans)
    else:
	pred,html_out = grade_and_explain(feedback)
	return render_template('autograde.html',html_out=html_out, 
						pred=pred, 
						feedback = feedback,
						qlist=qlist,
					    	ques=ques,
					    	question=question,
					    	model_ans=model_ans,
						selected=selected)

    if request.method == "POST":
	return render_template('index.html',ans=ans,
					    qlist=qlist,
					    ques=ques,
					    question=question,
					    model_ans=model_ans,
					    selected=selected)

@app.route("/feedback", methods=['GET', 'POST'])
def handle_feedback():
    global correct_phrases,incorrect_phrases,y_pred,X_test
    global vocab_corr, vocab_incorr, html_out, pred
    global selected, qlist, ques, question, model_ans
    global true_grades, feedback_green, feedback_red, end
 
    human_label = request.form['pred']
    feedback_correct = request.form['positive']
    feedback_incorrect = request.form['negative']

    if human_label=='no':
	if y_pred[0]=='Correct':            
	    true_pred = 'Incorrect'                
        else:
            true_pred = 'Correct'
    else:
	true_pred = y_pred[0]

    true_grades.append(true_pred)

    if not feedback_correct:
	print "No correction for blue phrases provided for this answer"
    else:
	feedback_correct = [x.strip() for x in feedback_correct.split(",")]

    if not feedback_incorrect:
	print "No correction for orange phrases provided for this answer"
    else:
	feedback_incorrect = [x.strip() for x in feedback_incorrect.split(",")]

    
    for phrase in feedback_correct:
	vocab_corr.append(phrase)

    for phrase in feedback_incorrect:
	vocab_incorr.append(phrase)

    correct_phrases,incorrect_phrases = correction_after_feedback(feedback_correct,feedback_incorrect)

    if end=="End":
	create_output_csv()

    if request.method == "POST":
	x_test = X_test[0]
	pred = true_pred
	saved_grades[x_test] = pred
	html_out = Markup(as_html_op(x_test,y_pred[0]))
	feedback_correct = ', '.join(feedback_correct)
	feedback_incorrect = ', '.join(feedback_incorrect)
	y_pred[0] = pred
	return render_template('autograde.html',html_out=html_out, 
						pred=pred, 
						human_label=human_label,
						feedback_incorrect=feedback_incorrect,
						feedback_correct=feedback_correct,
						feedback = "True",
						qlist=qlist,
					    	ques=ques,
					    	question=question,
					    	model_ans=model_ans,
						selected=selected)

@app.route("/next", methods=['GET', 'POST'])
def postfeedback():
    global correct_phrases, incorrect_phrases, X_train, y_train, X_test, y_pred
    global vocab_corr, vocab_incorr, html_out, pred
    global selected, qlist, ques, question, model_ans
    global saved_ans, given_grades, end

    end = None
    feedback = "True"
    if len(X_test)>1:
	x_test = X_test[0]
	X_train.append(x_test)
	y_train.append(y_pred[0])
	X_test.remove(x_test)

	if len(X_test) == 1:
	    end = "End" 
	
    	pred,html_out = grade_and_explain(feedback)

    	for phrase in vocab_corr:
	    if phrase not in correct_phrases:
	        correct_phrases.append(phrase)

    	for phrase in vocab_incorr:
	    if phrase not in incorrect_phrases:
	        incorrect_phrases.append(phrase)
    else:
	end = "End" 

    if request.method == "POST":
	return render_template('autograde.html',html_out=html_out, 
						pred=pred, 
						feedback = "False", 
						end=end,
						qlist=qlist,
					    	ques=ques,
					    	question=question,
					    	model_ans=model_ans,
						selected=selected)

if __name__ == '__main__':
    app.run(debug=True)
