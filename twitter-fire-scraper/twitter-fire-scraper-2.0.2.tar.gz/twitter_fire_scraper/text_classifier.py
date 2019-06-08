import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.svm import LinearSVC

fire = pd.read_csv("toy_dataset1.csv")

X_train, X_test, y_train, y_test = train_test_split(fire['Tweet'],fire['label'],test_size=0.3)

count_vect = CountVectorizer()
X_train_counts = count_vect.fit_transform(X_train)
tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
clf = LinearSVC().fit(X_train_tfidf, y_train)

# print(clf.predict(count_vect.transform(["text_here"])))

def classifier(text):
    result = clf.predict(count_vect.transform([text]))
    # print(result)
    return result